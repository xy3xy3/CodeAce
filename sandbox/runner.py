"""Container-side process supervisor. Never receives expected answers or verdicts."""
import sys,json,subprocess,os,time,resource,signal
LIMIT=128*1024
job=json.loads(sys.stdin.buffer.readline(2*1024*1024))
source=job['source']; language=job['language']; timeout=job.get('timeMs',3000)/1000
os.chdir('/work')
def limits():
    os.setsid()
    resource.setrlimit(resource.RLIMIT_CPU,(max(1,int(timeout)+1),max(2,int(timeout)+2)))
    resource.setrlimit(resource.RLIMIT_FSIZE,(8*1024*1024,8*1024*1024))
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
def execute(args,stdin,wall):
    start=time.monotonic()
    # Files are bounded by RLIMIT_FSIZE; stdout cannot exhaust supervisor RAM.
    with open('stdout','wb') as out,open('stderr','wb') as err:
        p=subprocess.Popen(args,stdin=subprocess.PIPE,stdout=out,stderr=err,preexec_fn=limits,env={**os.environ,'HOME':'/work','TMPDIR':'/work'})
        try: p.communicate(stdin.encode(),timeout=wall)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid,signal.SIGKILL);p.wait()
            return {'exit':-9,'timeout':True,'stdout':'','stderr':'超过时间限制','timeMs':round((time.monotonic()-start)*1000)}
    size=os.path.getsize('stdout')+os.path.getsize('stderr')
    return {'exit':p.returncode,'stdout':open('stdout','rb').read(LIMIT).decode('utf8',errors='replace'),'stderr':open('stderr','rb').read(LIMIT).decode('utf8',errors='replace'),'outputLimit':size>LIMIT,'timeMs':round((time.monotonic()-start)*1000),'memoryKb':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss}
if language=='cpp17':
    open('main.cpp','w').write(source+'\n'+job.get('harness',''))
    r=execute(['g++','-std=c++17','-O2','-pipe','main.cpp','-o','main'],'',20)
    if r['exit']!=0 or r.get('timeout'):
        r['compileError']=True;print(json.dumps(r));sys.exit()
    args=['/work/main']
else:
    open('main.py','w').write(source+'\n'+job.get('harness',''))
    args=['python3','-B','main.py']
r=execute(args,job.get('input',''),timeout)
print(json.dumps(r,ensure_ascii=False))
