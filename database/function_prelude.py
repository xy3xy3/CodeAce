from __future__ import annotations
from typing import *
from collections import deque,defaultdict,Counter,OrderedDict
import json,sys,ast,re,heapq,math,itertools,functools,bisect
class ListNode:
    def __init__(self,val=0,next=None):self.val,self.next=val,next
class TreeNode:
    def __init__(self,val=0,left=None,right=None):self.val,self.left,self.right=val,left,right
class Node:
    def __init__(self,val=0,next=None,random=None):self.val,self.next,self.random=val,next,random

def _ca_list(a):
    nodes=[ListNode(x) for x in a]
    for x,y in zip(nodes,nodes[1:]):x.next=y
    return (nodes[0] if nodes else None),nodes

def _ca_tree(a):
    if not a or a[0] is None:return None
    root=TreeNode(a[0]);q=deque([root]);i=1
    while q and i<len(a):
        n=q.popleft()
        for side in ['left','right']:
            if i>=len(a):break
            if a[i] is not None:
                x=TreeNode(a[i]);setattr(n,side,x);q.append(x)
            i+=1
    return root

def _ca_find(root,v):
    if root is None:return None
    if root.val==v:return root
    return _ca_find(root.left,v) or _ca_find(root.right,v)

def _ca_out(x):
    if isinstance(x,TreeNode):
        a=[];q=deque([x])
        while q:
            n=q.popleft();a.append(None if n is None else n.val)
            if n:q.extend([n.left,n.right])
        while a and a[-1] is None:a.pop()
        return a
    if isinstance(x,Node):
        a=[];nodes=[];seen=set()
        while x and id(x) not in seen:seen.add(id(x));nodes.append(x);x=x.next
        return [[n.val,nodes.index(n.random) if n.random in nodes else None] for n in nodes]
    if isinstance(x,ListNode):
        a=[];seen=set()
        while x and id(x) not in seen:seen.add(id(x));a.append(x.val);x=x.next
        return a
    if hasattr(x,'detach'):return x.detach().cpu().tolist()
    if hasattr(x,'tolist'):return x.tolist()
    return x

def _ca_values(s):
    try:
        x=json.loads(s)
        if isinstance(x,dict):return x
    except Exception:pass
    out={};parts=[];level=0;quote=None;escape=False;start=0
    for i,c in enumerate(s):
        if quote:
            if escape:escape=False
            elif c=='\\':escape=True
            elif c==quote:quote=None
        elif c in '\"\'':quote=c
        elif c in '[({':level+=1
        elif c in '])}':level-=1
        elif (c==',' or c=='\n') and level==0:parts.append(s[start:i]);start=i+1
    parts.append(s[start:])
    for part in parts:
        if not part.strip():continue
        name,sep,value=part.partition('=')
        if not sep or not re.fullmatch(r'[A-Za-z_]\w*',name.strip()):raise ValueError('函数输入应为 JSON 对象或 name = value')
        class Literals(ast.NodeTransformer):
            def visit_Name(self,node):
                mapping={'null':None,'true':True,'false':False}
                return ast.copy_location(ast.Constant(mapping[node.id]),node) if node.id in mapping else node
        expression=Literals().visit(ast.parse(value.strip(),mode='eval'))
        out[name.strip()]=ast.literal_eval(expression)
    return out

def _ca_call(meta):
    raw=sys.stdin.read();pid=meta['id']
    if meta.get('design'):
        try:
            j=json.loads(raw);ops,args=(j['operations'],j['arguments']) if isinstance(j,dict) else j
        except Exception:
            lines=raw.strip().splitlines();ops=json.loads(lines[0]);args=json.loads(lines[1])
        obj=globals()[ops[0]](*args[0]);ans=[None]
        for op,arg in zip(ops[1:],args[1:]):ans.append(getattr(obj,op)(*arg))
        print(json.dumps(ans,ensure_ascii=False));return
    vals=_ca_values(raw);params=meta['params'];args=[];nodes_by_name={};original_random_nodes=[]
    if pid==1493:
        aa=vals['headA'];bb=vals['headB'];common=0
        while common<min(len(aa),len(bb)) and aa[-1-common]==bb[-1-common]:common+=1
        shared,_=_ca_list(aa[len(aa)-common:] if common else [])
        for key,a in [('headA',aa),('headB',bb)]:
            head,ns=_ca_list(a[:len(a)-common] if common else a)
            if ns:ns[-1].next=shared
            else:head=shared
            vals[key]=head
    for param in params:
        name,kind=param['name'],param['type'];v=vals.get(name)
        if kind=='ListNode' and isinstance(v,list):
            v,ns=_ca_list(v);nodes_by_name[name]=ns
            if pid in [1496,1497] and ns and vals.get('pos',-1)>=0:ns[-1].next=ns[vals['pos']]
        elif kind=='ListNode[]':v=[_ca_list(a)[0] for a in v]
        elif kind=='TreeNode':
            v=_ca_tree(v) if isinstance(v,list) else _ca_find(vals.get('root'),v)
            if name=='root':vals['root']=v
        elif kind=='Node':
            ns=[Node(x[0]) for x in v]
            for i,n in enumerate(ns):
                n.next=ns[i+1] if i+1<len(ns) else None;n.random=ns[v[i][1]] if v[i][1] is not None else None
            original_random_nodes=ns[:]
            v=ns[0] if ns else None
        args.append(v)
    if pid==1520:
        obj=Codec();ans=obj.deserialize(obj.serialize(args[0]))
    else:ans=getattr(Solution(),meta['method'])(*args)
    if pid==1503:
        n=ans;copied=[]
        while n and n not in copied:
            if n in original_random_nodes:raise ValueError('深拷贝必须返回新节点，不能返回原链表节点')
            copied.append(n);n=n.next
        if any(n.random is not None and n.random not in copied for n in copied):raise ValueError('random 指针必须指向复制后的节点')
    if meta.get('inplace'):ans=args[0]
    if ans is None and meta.get('returnType') in ['ListNode','TreeNode','Node'] and pid not in [1493,1497]:ans=[]
    if pid==1493:ans=None if ans is None else ans.val
    if pid==1497:
        ns=nodes_by_name.get('head',[]);ans=ns.index(ans) if ans in ns else -1
    if pid==1516:ans=ans.val if isinstance(ans,TreeNode) else ans
    print(json.dumps(_ca_out(ans),ensure_ascii=False))
