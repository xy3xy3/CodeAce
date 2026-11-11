"""Trusted original exercise authoring and fixture verifier; never downloads source tasks.

Regenerate: docker run --rm --user 0 --entrypoint python3 -v "$PWD:/work" -w /work \
  codeace-runtime:local database/deep-reference.py --write
Verify all complete harnesses and mathematical invariants: same command without --write.
Only the authored reference implementations below are executed.
"""
import argparse
import copy
import json
import math
from pathlib import Path
import torch
import torch.nn.functional as F

torch.set_num_threads(1)
torch.set_default_dtype(torch.float64)
ROOT = Path(__file__).resolve().parent.parent
PRELUDE = '''import torch
import torch.nn.functional as F

def T(value):
    return torch.tensor(value, dtype=torch.float64)
'''
HARNESS = '''import json
import sys

def _json_value(value):
    if isinstance(value, torch.Tensor):
        return value.detach().cpu().tolist()
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value

print(json.dumps(_json_value(solve(json.loads(sys.stdin.read()))), allow_nan=False))
'''
ENTRIES = []


def add(id, title, contract, output, code, cases, complexity='O(N) 时间，O(N) 输出空间，N 为输入元素数。', doc='nn.functional.html', difficulty='中等', explanation='逐项按题设公式计算；使用 float64 保留数值精度，返回张量时保留所有轴。'):
    assert len(cases) >= 3
    ENTRIES.append(dict(id=id, title=title, contract=contract, output=output, code=code.strip()+'\n', cases=cases, complexity=complexity, doc=doc, difficulty=difficulty, explanation=explanation))


ACTIVATION_CASES = [dict(x=[[-1000., -2., 0., 2., 1000.]], alpha=0.2, beta=1.3), dict(x=[[-3., -0.1], [0.3, 3.]], alpha=0.05, beta=0.7), dict(x=[[[0.], [-1.5]], [[2.5], [-0.001]]], alpha=0.4, beta=2.)]
# The exercise statements explicitly define variant constants; no external problem text is used.
for id, title, formula, expression in [
    (1615, 'Leaky ReLU', 'f(x)=x（x≥0），否则为 alpha*x。', 'torch.where(x >= 0, x, data["alpha"] * x)'),
    (1622, 'Sigmoid', 'f(x)=1/(1+exp(-x))，需在 ±1000 时保持有限。', 'torch.sigmoid(x)'),
    (1624, 'ReLU', 'f(x)=max(x,0)。', 'x.clamp_min(0)'),
    (1631, 'Hard Sigmoid', 'f(x)=clip(x/6+1/2,0,1)。', '(x/6+0.5).clamp(0,1)'),
    (1632, 'ELU', 'f(x)=x（x>0），否则为 alpha*(exp(x)-1)。', 'torch.where(x > 0, x, data["alpha"] * torch.expm1(x.clamp_max(0)))'),
    (1633, 'PReLU', '通道轴为轴 1；f(x[n,c,...])=max(x,0)+a[c]*min(x,0)。', 'x.clamp_min(0) + T(data["a"]).reshape(1,-1,*([1]*(x.ndim-2))) * x.clamp_max(0)'),
    (1634, 'Softplus', 'f(x)=log(1+exp(beta*x))/beta，beta>0；需数值稳定。', 'F.softplus(x, beta=data["beta"], threshold=30)'),
    (1635, 'Softsign', 'f(x)=x/(1+|x|)。', 'x/(1+x.abs())'),
    (1636, 'Swish', 'f(x)=x*sigmoid(beta*x)。', 'x*torch.sigmoid(data["beta"]*x)'),
    (1637, 'SELU', '取 alpha=1.6732632423543772，scale=1.0507009873554805；f(x)=scale*x（x>0），否则 scale*alpha*(exp(x)-1)。', '1.0507009873554805*torch.where(x>0,x,1.6732632423543772*torch.expm1(x.clamp_max(0)))'),
]:
    cases = copy.deepcopy(ACTIVATION_CASES)
    fields = 'x：1～4 维非空实数数组；alpha、beta：正实数（只在对应公式出现时使用）。'
    if id == 1633:
        cases = [dict(x=[[-2., 3.], [4., -5.]], a=[0.1,0.3]), dict(x=[[[-2.,0.,1.],[3.,-4.,2.]]],a=[0.,0.5]), dict(x=[[[[-1.]],[[2.]], [[-3.]]]],a=[0.2,0.4,0.8])]
        fields = 'x：形状 [B,C,...]（至少二维）；a：长度 C 的通道斜率数组。'
    add(id,title, fields+'\n'+formula,'返回与 x 形状相同的激活张量。',f'def solve(data):\n    x = T(data["x"])\n    return {expression}',cases,difficulty='简单')

for id,title,dim,variant in [(1614,'Log-Softmax',-1,'log'),(1623,'数值稳定 Softmax 函数',-1,'prob'),(3705,'数值稳定 Softmax 归一化',1,'prob'),(3718,'Softmax Stable',0,'prob')]:
    add(id,title,f'x：二维非空 logits [R,C]，数值可达 ±10000。沿轴 {dim} 计算'+('log softmax：x-log(sum(exp(x)))，必须先减去该轴最大值。' if variant=='log' else 'softmax：exp(x-max)/sum(exp(x-max))。'), '返回形状 [R,C] 的归一化结果；不压缩单元素轴。',f'''def solve(data):
    x = T(data["x"])
    shifted = x - x.amax(dim={dim}, keepdim=True)
    log_den = shifted.exp().sum(dim={dim}, keepdim=True).log()
    return shifted - log_den{' ' if variant=='log' else ''}
''' if variant=='log' else f'''def solve(data):
    x = T(data["x"])
    e = (x - x.amax(dim={dim}, keepdim=True)).exp()
    return e/e.sum(dim={dim}, keepdim=True)
''',[dict(x=[[10000,9999,-10000],[1,2,3]]),dict(x=[[-10000,-10000],[5,-5],[0,0]]),dict(x=[[12.],[0.],[-20.]])],difficulty='简单',explanation='先平移最大值，指数均不超过 1；对数版本直接使用 shifted-log(sum(exp(shifted)))，避免对下溢的概率取对数。')

CE_CASES = [dict(logits=[[1000,999,-1000],[-2,0,3]],labels=[0,1],smoothing=0.1),dict(logits=[[0,0],[2,-1],[-1,4]],labels=[1,0,1],smoothing=0.25),dict(logits=[[3]],labels=[0],smoothing=0.)]
for id,title,reduction,smooth in [(1625,'多分类交叉熵损失计算','none',False),(1819,'多类交叉熵样本平均损失','mean',False),(3719,'交叉熵损失函数','sum',False),(3837,'标签平滑交叉熵损失','mean',True)]:
    formula = '令 q=(1-smoothing)*one_hot(label)+smoothing/C，计算 mean_i(-sum_c q[i,c]*log_softmax(logits)[i,c]))。' if smooth else f'每项 L[i]=-log_softmax(logits)[i,labels[i]]；输出规约方式为 {reduction}（none 表示不规约，mean 为平均，sum 为求和）。'
    add(id,title,'logits：[B,C]，labels：B 个从 0 开始的合法类别。'+('smoothing∈[0,1]。' if smooth else '')+'\n'+formula,'返回 '+('[B] 损失向量。' if reduction=='none' else '一个浮点标量损失。'),f'''def solve(data):
    x = T(data["logits"])
    lp = x-torch.logsumexp(x, dim=1, keepdim=True)
    labels = torch.tensor(data["labels"], dtype=torch.long)
    nll = -lp[torch.arange(x.shape[0]), labels]
    loss = {( '(1-data["smoothing"])*nll-data["smoothing"]*lp.mean(dim=1)' if smooth else 'nll')}
    return {('loss' if reduction=='none' else 'loss.'+reduction+'()')}
''',copy.deepcopy(CE_CASES),complexity='O(B*C) 时间与空间。',explanation='logsumexp 直接从 logits 计算对数概率，避免先算 softmax 再取 log。标签平滑将剩余权重均匀分给包括正确类别在内的所有类别。')

add(3720,'离散 KL 散度计算','p、q：形状 [B,C]，每行均是概率分布；p≥0，q>0。逐行计算 D_KL(p||q)=sum p*log(p/q)，约定 0*log(0/q)=0。','返回长度 B 的 KL 向量。','''def solve(data):
    p, q = T(data["p"]), T(data["q"])
    return torch.where(p > 0, p*(p.clamp_min(1e-300).log()-q.log()), 0.).sum(dim=1)
''',[dict(p=[[0,1],[0.3,0.7]],q=[[0.5,0.5],[0.6,0.4]]),dict(p=[[0.2,0.3,0.5]],q=[[0.2,0.3,0.5]]),dict(p=[[1,0,0],[0,0,1]],q=[[0.8,0.1,0.1],[0.2,0.3,0.5]])])

add(1638,'单神经元二分类前向传播与均方误差','x：[B,D]，w：[D]，b：标量，target：[B]。计算 prediction=sigmoid(x@w+b)，MSE=mean((prediction-target)^2)。','返回对象 {prediction: [B], loss: 标量}。','''def solve(data):
    p = torch.sigmoid(T(data["x"])@T(data["w"])+data["b"])
    return {"prediction":p,"loss":((p-T(data["target"]))**2).mean()}
''',[dict(x=[[1,2],[-1,0]],w=[0.2,-0.3],b=0.1,target=[1,0]),dict(x=[[1000],[-1000],[0]],w=[2],b=0,target=[1,0,0.5]),dict(x=[[1,0,-1]],w=[0,1,2],b=-0.5,target=[0.3])],complexity='O(B*D) 时间，O(B) 额外空间。')

# Normalization: all variance estimates use divisor K, not K-1.
NORM_CASES = [dict(x=[[[[1.,2.],[3.,5.]],[[2.,0.],[-2.,4.]]],[[[3.,1.],[0.,-1.]],[[6.,2.],[1.,3.]]]],weight=[1.2,0.7],bias=[-0.1,0.3],eps=1e-5,groups=2),dict(x=[[[[2.,2.]],[[1.,3.]],[[0.,4.]],[[2.,-2.]]]],weight=[1,2,0.5,-1],bias=[0,0.1,-0.2,0.3],eps=0.01,groups=2),dict(x=[[[[7.]], [[-3.]]]],weight=[1,2],bias=[0.2,-0.4],eps=0.001,groups=1)]
for id,title,kind in [(1627,'BatchNorm2d','batch'),(1641,'GroupNorm','group'),(1642,'InstanceNorm','instance'),(1820,'GroupNorm Simple','group-simple')]:
    axes = {'batch':'每个通道在 B、H、W 轴上统计均值与方差（训练态，不维护 running statistics）。','group':'把 C 通道分成 groups 组，每个样本每组在 C/groups、H、W 上统计。','instance':'每个样本每通道在 H、W 上统计。','group-simple':'把 C 通道分成 groups 组，每个样本每组在 C/groups、H、W 上统计；本题不使用仿射变换。'}[kind]
    code = '''def solve(data):
    x = T(data["x"])
'''
    if kind=='batch':code+='    mean = x.mean(dim=(0,2,3), keepdim=True)\n    var = x.var(dim=(0,2,3), unbiased=False, keepdim=True)\n    y = (x-mean)/torch.sqrt(var+data["eps"])\n'
    elif kind=='instance':code+='    mean = x.mean(dim=(2,3), keepdim=True)\n    var = x.var(dim=(2,3), unbiased=False, keepdim=True)\n    y = (x-mean)/torch.sqrt(var+data["eps"])\n'
    else:code+='    z = x.reshape(x.shape[0],data["groups"],-1)\n    y = ((z-z.mean(dim=-1,keepdim=True))/torch.sqrt(z.var(dim=-1,unbiased=False,keepdim=True)+data["eps"])).reshape_as(x)\n'
    code+=('    return y\n' if kind=='group-simple' else '    return y*T(data["weight"])[None,:,None,None]+T(data["bias"])[None,:,None,None]\n')
    add(id,title,'x：[B,C,H,W]；groups 为 C 的正因子；eps>0；weight、bias：[C]。'+axes+'所有方差使用总体方差（除以元素个数），标准化分母为 sqrt(var+eps)。除 Simple 外，最后按通道计算 y*weight+bias。','返回形状与 x 相同的标准化结果。',code,copy.deepcopy(NORM_CASES))

add(1628,'LayerNorm','x：[B,S,D]，weight、bias：[D]，eps>0。每个 (b,s) 位置沿 D 轴计算总体方差，返回 (x-mean)/sqrt(var+eps)*weight+bias。','返回形状 [B,S,D] 的张量。','''def solve(data):
    x = T(data["x"])
    return (x-x.mean(-1,keepdim=True))/torch.sqrt(x.var(-1,unbiased=False,keepdim=True)+data["eps"])*T(data["weight"])+T(data["bias"])
''',[dict(x=[[[1,2,4],[0,0,0]],[[5,-1,2],[9,3,6]]],weight=[1,2,0.5],bias=[0.2,-0.1,0.3],eps=1e-5),dict(x=[[[1]],[[3]]],weight=[2],bias=[-1],eps=0.01),dict(x=[[[1,-1],[1.001,1]]],weight=[-1,0.4],bias=[0,2],eps=0.1)])

add(1824,'InstanceNorm1d','x：[B,C,L]，weight、bias：[C]，eps>0。对每个样本的每个通道沿 L 计算总体均值、方差，标准化后作通道仿射变换。','返回形状 [B,C,L] 的张量。','''def solve(data):
    x = T(data["x"])
    y = (x-x.mean(-1,keepdim=True))/torch.sqrt(x.var(-1,unbiased=False,keepdim=True)+data["eps"])
    return y*T(data["weight"])[None,:,None]+T(data["bias"])[None,:,None]
''',[dict(x=[[[1,3,5],[2,0,-2]],[[3,2,1],[4,4,4]]],weight=[2,0.5],bias=[1,-1],eps=1e-5),dict(x=[[[3]], [[-1]]],weight=[1.5],bias=[0.2],eps=0.01),dict(x=[[[1,1.001],[2,2.002]]],weight=[1,-1],bias=[0,1],eps=0.1)])

add(3696,'BatchNorm Forward','x：[B,D]，weight、bias、running_mean、running_var：[D]；training：布尔值；momentum∈[0,1]，eps>0。训练时输出使用 batch 总体方差，但更新 running_var 使用无偏样本方差；B≥2。new=(1-momentum)*old+momentum*batch。推理时使用 running 统计，且不更新。','返回 {y:[B,D], running_mean:[D], running_var:[D]}。','''def solve(data):
    x = T(data["x"])
    rm, rv = T(data["running_mean"]), T(data["running_var"])
    if data["training"]:
        mean, var = x.mean(0), x.var(0, unbiased=False)
        m = data["momentum"]
        new_mean = (1-m)*rm+m*mean
        new_var = (1-m)*rv+m*x.var(0,unbiased=True)
    else:
        mean, var = rm, rv
        new_mean, new_var = rm, rv
    y = (x-mean)/torch.sqrt(var+data["eps"])*T(data["weight"])+T(data["bias"])
    return {"y":y,"running_mean":new_mean,"running_var":new_var}
''',[dict(x=[[1,2],[3,6],[5,1]],weight=[1.2,0.8],bias=[0.1,-0.2],running_mean=[0,2],running_var=[1,3],momentum=0.2,eps=1e-5,training=True),dict(x=[[2,2],[2,2]],weight=[1,1],bias=[1,-1],running_mean=[3,4],running_var=[2,5],momentum=1.,eps=0.01,training=True),dict(x=[[5,-2]],weight=[2,0.5],bias=[1,0],running_mean=[1,2],running_var=[4,1],momentum=0.3,eps=0.001,training=False)],complexity='O(B*D) 时间，O(B*D+D) 空间。')

add(1629,'Global Average Pooling','x：[B,C,H,W]，H、W 为正整数。对每个样本每个通道在全部空间位置取均值；本题保留空间单元素维度。','返回形状 [B,C,1,1] 的张量。','''def solve(data):
    return T(data["x"]).mean(dim=(2,3),keepdim=True)
''',[dict(x=c['x']) for c in NORM_CASES],difficulty='简单')

CONV_CASES = [dict(x=[[[[1,2,3],[4,5,6],[7,8,9]]]],w=[[[[1,0],[0,-1]]],[[[0,1],[2,0]]]],b=[0.5,-1],stride=[1,1],padding=[0,0],dilation=[1,1],groups=1),dict(x=[[[[1,2],[3,4]],[[0,1],[-1,2]]]],w=[[[[1]]],[[[-2]]]],b=[0,1],stride=[2,1],padding=[1,0],dilation=[1,1],groups=2),dict(x=[[[[1,2,0],[0,-1,3],[2,1,-2]],[[2,0,1],[1,2,0],[0,-1,2]]]],w=[[[[1,2],[0,-1]],[[0,1],[2,0]]]],b=[0.2],stride=[1,1],padding=[1,1],dilation=[2,2],groups=1)]
CONV_CONTRACT='x：[B,Cin,H,W]；w：[Cout,Cin/groups,Kh,Kw]；b：[Cout]；stride、padding、dilation：两个整数；groups 整除 Cin、Cout。采用 PyTorch 的互相关（核不翻转），零填充，不使用 ceil。'
add(1630,'Conv2D',CONV_CONTRACT,'返回卷积输出 [B,Cout,Hout,Wout]。','''def solve(data):
    return F.conv2d(T(data["x"]),T(data["w"]),T(data["b"]),stride=data["stride"],padding=data["padding"],dilation=data["dilation"],groups=data["groups"])
''',copy.deepcopy(CONV_CASES),complexity='O(B*Cout*Hout*Wout*(Cin/groups)*Kh*Kw) 时间；O(输出元素数) 空间。',doc='generated/torch.nn.Conv2d.html')
add(5566,'Conv2D Forward and Backward',CONV_CONTRACT+'令标量目标 L=sum(output^2)/2。计算对 x、w、b 的精确梯度，允许使用 autograd。','返回 {y:卷积输出, dx:与 x 同形, dw:与 w 同形, db:[Cout]}。','''def solve(data):
    x,w,b = [T(data[k]).requires_grad_() for k in ("x","w","b")]
    y = F.conv2d(x,w,b,stride=data["stride"],padding=data["padding"],dilation=data["dilation"],groups=data["groups"])
    dx,dw,db = torch.autograd.grad(y.square().sum()/2,(x,w,b))
    return {"y":y,"dx":dx,"dw":dw,"db":db}
''',copy.deepcopy(CONV_CASES),complexity='前后向时间 O(B*Cout*Hout*Wout*(Cin/groups)*Kh*Kw)，空间为输入、权重和输出元素数之和。',doc='generated/torch.nn.Conv2d.html',difficulty='困难',explanation='先构建可求导的输入和权重，再对 L=1/2||y||² 反传。上游梯度正是 y，权重共享会使多个位置的梯度累加。')

add(1810,'二维卷积输出空间尺寸计算','shape=[H,W]，kernel、stride、padding、dilation 均为长度 2 的整数数组。逐轴计算 out=floor((in+2*padding-dilation*(kernel-1)-1)/stride)+1。保证最终尺寸为正。','返回两个整数 [Hout,Wout]。','''def solve(data):
    return [(n+2*p-d*(k-1)-1)//s+1 for n,k,s,p,d in zip(data["shape"],data["kernel"],data["stride"],data["padding"],data["dilation"])]
''',[dict(shape=[7,9],kernel=[3,2],stride=[2,3],padding=[1,0],dilation=[1,2]),dict(shape=[5,4],kernel=[1,3],stride=[1,2],padding=[0,2],dilation=[2,1]),dict(shape=[11,8],kernel=[3,2],stride=[3,2],padding=[2,1],dilation=[2,3])],complexity='O(1) 时间与空间。',difficulty='简单',doc='generated/torch.nn.Conv2d.html')

add(1801,'MaxPool2d','x：[B,C,H,W]；kernel、stride、padding：二维整数数组；使用零以外的负无穷填充、floor 模式，dilation=1。每个窗口取最大值，保证每个输出窗口包含输入元素。','返回形状 [B,C,Hout,Wout] 的池化张量。','''def solve(data):
    return F.max_pool2d(T(data["x"]),data["kernel"],stride=data["stride"],padding=data["padding"],ceil_mode=False)
''',[dict(x=[[[[-4,-3,-8],[-1,-7,-2],[0,2,1]]]],kernel=[2,2],stride=[1,2],padding=[1,1]),dict(x=[[[[1,3,2,4],[5,0,6,-1]]]],kernel=[1,2],stride=[1,1],padding=[0,0]),dict(x=[[[[3]]],[[[-5]]]],kernel=[1,1],stride=[1,1],padding=[0,0])],complexity='O(B*C*Hout*Wout*Kh*Kw) 时间，O(输出元素数) 空间。',doc='generated/torch.nn.MaxPool2d.html')

add(1802,'Huber Loss','prediction、target：相同形状数组；delta>0。令 e=prediction-target；当 |e|≤delta 时 L=e²/2，否则 L=delta*(|e|-delta/2)；最终对所有元素取平均。','返回一个标量平均损失。','''def solve(data):
    e = T(data["prediction"])-T(data["target"])
    d = data["delta"]
    return torch.where(e.abs()<=d,e.square()/2,d*(e.abs()-d/2)).mean()
''',[dict(prediction=[[-2,0,2],[0.5,1,-1]],target=[[0,0,0],[0,0,0]],delta=1),dict(prediction=[3,-2,1],target=[2,-1,1],delta=0.5),dict(prediction=[[[0.1,-0.2]]],target=[[[0.15,0.1]]],delta=2)],doc='generated/torch.nn.HuberLoss.html')

add(1803,'带确定性种子的 Dropout 前向传播','x：任意非空数组；p∈[0,1)，seed：整数。训练态：创建独立 CPU torch.Generator().manual_seed(seed)，以 torch.rand(x.shape,generator=g,dtype=torch.float64) 按行优先顺序生成随机数；保留 random≥p 的元素并除以 1-p。training=false 则原样返回，不消耗全局随机状态。','返回 {y:与 x 同形, mask:同形 0/1 数组}；推理态 mask 全为 1。','''def solve(data):
    x = T(data["x"])
    if not data["training"]:
        mask = torch.ones_like(x)
    else:
        g = torch.Generator(device="cpu").manual_seed(data["seed"])
        mask = (torch.rand(x.shape,generator=g,dtype=torch.float64)>=data["p"]).to(x.dtype)
    y = x*mask/(1-data["p"]) if data["training"] else x
    return {"y":y,"mask":mask}
''',[dict(x=[[1,2,-3],[4,0,6]],p=0.4,seed=42,training=True),dict(x=[[[1,-2],[3,4]]],p=0.75,seed=7,training=True),dict(x=[[1,-1]],p=0.5,seed=42,training=False)],doc='generated/torch.nn.Dropout.html')
add(3695,'给定掩码的 Dropout 缩放计算','x、mask：相同形状，mask 元素为 0 或 1；p∈[0,1)，training：布尔。训练态 y=x*mask/(1-p)，推理态 y=x；不生成随机数。','返回与 x 形状相同的输出张量。','''def solve(data):
    x = T(data["x"])
    return x*T(data["mask"])/(1-data["p"]) if data["training"] else x
''',[dict(x=[[1,-2,3],[4,5,6]],mask=[[1,0,1],[0,1,0]],p=0.25,training=True),dict(x=[[[1],[2]]],mask=[[[0],[1]]],p=0.,training=True),dict(x=[[-3,4]],mask=[[0,0]],p=0.9,training=False)],difficulty='简单',doc='generated/torch.nn.Dropout.html')

add(1645,'Dynamic Tanh','x：[B,S,D]；alpha：标量；weight、bias：[D]。实现无统计量的 DyT 层 y=weight*tanh(alpha*x)+bias，沿最后一轴广播仿射参数。','返回形状 [B,S,D] 的张量。','''def solve(data):
    return torch.tanh(data["alpha"]*T(data["x"]))*T(data["weight"])+T(data["bias"])
''',[dict(x=[[[1,-2],[3,0]]],alpha=0.5,weight=[2,0.3],bias=[0.1,-0.2]),dict(x=[[[1000],[-1000]],[[0],[2]]],alpha=2,weight=[1.5],bias=[0.2]),dict(x=[[[1,2,3]]],alpha=0,weight=[1,2,3],bias=[3,2,1])],doc='generated/torch.tanh.html')

# Optimizers expose optimizer state so a stateless or uncorrected update cannot pass.
OPT_CASES = [dict(param=[[1.,-2.],[0.5,3.]],grad=[[0.2,-0.4],[0.,0.6]],m=[[0.1,-0.2],[0.3,0]],v=[[0.4,0.2],[0.1,0.5]],lr=0.03,beta1=0.8,beta2=0.9,eps=1e-6,step=4,momentum=0.7,rho=0.8,weight_decay=0.02),dict(param=[0.,2.,-3.],grad=[-0.5,0.,1.],m=[0.,0.,0.],v=[0.,0.,0.],lr=0.1,beta1=0.9,beta2=0.99,eps=1e-8,step=1,momentum=0.,rho=0.95,weight_decay=0.),dict(param=[[[2.],[-1.]]],grad=[[[0.01],[-0.03]]],m=[[[0.2],[-0.1]]],v=[[[0.03],[0.04]]],lr=0.005,beta1=0.7,beta2=0.8,eps=0.01,step=12,momentum=0.9,rho=0.6,weight_decay=0.1)]
OPT_COMMON='param、grad、m、v：同形状张量；m 是一阶状态，v 是非负二阶状态（仅在公式出现时使用）。lr、eps>0；step≥1 是本次更新编号；beta1、beta2、momentum、rho∈[0,1)。'
for id,title in [(1646,'Adam Optimizer Step'),(3692,'向量化 Adam 优化步更新')]:
    add(id,title,OPT_COMMON+'\nAdam（无权重衰减）：m_new=beta1*m+(1-beta1)*grad，v_new=beta2*v+(1-beta2)*grad²；偏差修正 m_hat=m_new/(1-beta1^step)、v_hat=v_new/(1-beta2^step)；param_new=param-lr*m_hat/(sqrt(v_hat)+eps)。','返回 {param:更新后的参数,m:新一阶状态,v:新二阶状态}。','''def solve(data):
    p,g,m,v = [T(data[k]) for k in ("param","grad","m","v")]
    b1,b2,t = data["beta1"],data["beta2"],data["step"]
    m = b1*m+(1-b1)*g
    v = b2*v+(1-b2)*g.square()
    p = p-data["lr"]*(m/(1-b1**t))/(torch.sqrt(v/(1-b2**t))+data["eps"])
    return {"param":p,"m":m,"v":v}
''',copy.deepcopy(OPT_CASES),doc='generated/torch.optim.Adam.html',explanation='状态先更新再按当前 step 作偏差修正；eps 位于平方根外。即便梯度为零，非零历史动量仍会改变参数。')
for id,title in [(1648,'Momentum SGD Step'),(3691,'向量化动量 SGD 单步更新')]:
    add(id,title,OPT_COMMON+'\n本题缓冲区定义为 m_new=momentum*m+grad（不乘 1-momentum），param_new=param-lr*m_new；不使用权重衰减。','返回 {param:新参数,m:新动量}。','''def solve(data):
    m = data["momentum"]*T(data["m"])+T(data["grad"])
    return {"param":T(data["param"])-data["lr"]*m,"m":m}
''',copy.deepcopy(OPT_CASES),doc='generated/torch.optim.SGD.html')
add(1647,'Adagrad Step',OPT_COMMON+'\n累积平方梯度 v_new=v+grad²；param_new=param-lr*grad/(sqrt(v_new)+eps)。无 lr decay、无 weight decay。','返回 {param:新参数,v:新累积平方梯度}。','''def solve(data):
    g = T(data["grad"])
    v = T(data["v"])+g.square()
    return {"param":T(data["param"])-data["lr"]*g/(v.sqrt()+data["eps"]),"v":v}
''',copy.deepcopy(OPT_CASES),doc='generated/torch.optim.Adagrad.html')
add(1649,'Adamax Step',OPT_COMMON+'\n令 m_new=beta1*m+(1-beta1)*grad；u_new=max(beta2*v,abs(grad)+eps)，v 在本题代表无穷范数状态 u；param_new=param-lr/(1-beta1^step)*m_new/u_new。','返回 {param:新参数,m:新一阶状态,v:新无穷范数状态}。','''def solve(data):
    g = T(data["grad"])
    m = data["beta1"]*T(data["m"])+(1-data["beta1"])*g
    u = torch.maximum(data["beta2"]*T(data["v"]),g.abs()+data["eps"])
    return {"param":T(data["param"])-data["lr"]*m/((1-data["beta1"]**data["step"])*u),"m":m,"v":u}
''',copy.deepcopy(OPT_CASES),doc='generated/torch.optim.Adamax.html')
add(1650,'Adadelta Step',OPT_COMMON+'\n本题 v 是平方梯度滑动均值，m 是平方更新滑动均值（均非负）。v_new=rho*v+(1-rho)*grad²；delta=sqrt(m+eps)/sqrt(v_new+eps)*grad；param_new=param-lr*delta；m_new=rho*m+(1-rho)*delta²。','返回 {param:新参数,m:新平方更新均值,v:新平方梯度均值}。','''def solve(data):
    g,m,v = [T(data[k]) for k in ("grad","m","v")]
    rho,eps = data["rho"],data["eps"]
    v = rho*v+(1-rho)*g.square()
    delta = (m+eps).sqrt()/(v+eps).sqrt()*g
    return {"param":T(data["param"])-data["lr"]*delta,"m":rho*m+(1-rho)*delta.square(),"v":v}
''',[dict(c,m=torch.tensor(c['m']).abs().tolist()) for c in OPT_CASES],doc='generated/torch.optim.Adadelta.html')
add(5567,'Nesterov Accelerated Gradient',OPT_COMMON+'\n采用 PyTorch SGD 的 Nesterov 约定：g=grad+weight_decay*param；buffer_new=momentum*m+g（已有缓冲区）；方向 d=g+momentum*buffer_new；param_new=param-lr*d。不使用 dampening。','返回 {param:新参数,m:新缓冲区}。','''def solve(data):
    p = T(data["param"])
    g = T(data["grad"])+data["weight_decay"]*p
    m = data["momentum"]*T(data["m"])+g
    return {"param":p-data["lr"]*(g+data["momentum"]*m),"m":m}
''',copy.deepcopy(OPT_CASES),doc='generated/torch.optim.SGD.html',explanation='Nesterov 需要在更新缓冲区之后，再使用 grad+momentum*buffer；此约定不同于直接用缓冲区作为方向的普通 momentum。')

add(5568,'Exponential LR Scheduler','base_lr>0，gamma>0，epochs：非负整数数组。第 e 个训练轮的学习率定义为 base_lr*gamma^e，e=0 时为初始学习率；一次返回任意顺序的多个轮次。','返回与 epochs 等长的学习率数组。','''def solve(data):
    return [data["base_lr"]*data["gamma"]**e for e in data["epochs"]]
''',[dict(base_lr=0.1,gamma=0.9,epochs=[0,1,2,10]),dict(base_lr=0.003,gamma=1.2,epochs=[5,0,3]),dict(base_lr=0.5,gamma=0.5,epochs=[0,4,20])],complexity='O(E) 时间与空间，E 为请求轮次数。',doc='generated/torch.optim.lr_scheduler.ExponentialLR.html',difficulty='简单')
add(5569,'Cosine Annealing LR','base_lr≥eta_min≥0，t_max>0，epochs：非负整数数组。单周期余弦衰减：t=min(epoch,t_max)，lr=eta_min+(base_lr-eta_min)*(1+cos(pi*t/t_max))/2。超过 t_max 后固定在 eta_min，不重启。','返回与 epochs 等长的学习率数组。','''def solve(data):
    import math
    return [data["eta_min"]+(data["base_lr"]-data["eta_min"])*(1+math.cos(math.pi*min(e,data["t_max"])/data["t_max"]))/2 for e in data["epochs"]]
''',[dict(base_lr=0.1,eta_min=0.01,t_max=4,epochs=[0,1,2,4,8]),dict(base_lr=0.003,eta_min=0.,t_max=3,epochs=[2,0,1,3]),dict(base_lr=0.5,eta_min=0.5,t_max=1,epochs=[0,1,5])],complexity='O(E) 时间与空间。',doc='generated/torch.optim.lr_scheduler.CosineAnnealingLR.html',difficulty='简单')

ATTN_CASES = [dict(q=[[[1,0],[0,2],[1,-1]]],k=[[[0,1],[2,0],[-1,1]]],v=[[[1,2],[3,-1],[0,4]]],mask=[[[1,0,0],[1,1,0],[1,1,1]]],eps=1e-8,scale=2.),dict(q=[[[1,2]],[[0,-1]]],k=[[[2,1],[1,0]],[[1,1],[-1,2]]],v=[[[1],[3]],[[2],[-2]]],mask=[[[1,0]],[[1,1]]],eps=0.01,scale=0.7),dict(q=[[[0,0],[2,-1]]],k=[[[0,0],[1,1]]],v=[[[3,-2,1],[1,2,-3]]],mask=[[[0,1],[1,1]]],eps=1e-4,scale=1.5)]
add(1626,'带掩码的缩放点积自注意力','q：[B,S,D]、k：[B,S,D]、v：[B,S,Dv]；mask：[B,S,S]，1 表示允许关注，0 表示屏蔽，保证每行至少一个 1。计算 scores=q@k^T/sqrt(D)，先将被屏蔽位置设为负无穷，再在最后一轴 softmax；y=weights@v。','返回 {y:[B,S,Dv],weights:[B,S,S]}，屏蔽位置权重必须为 0。','''def solve(data):
    q,k,v = [T(data[key]) for key in ("q","k","v")]
    scores = q@k.transpose(-2,-1)/(q.shape[-1]**0.5)
    scores = scores.masked_fill(~torch.tensor(data["mask"],dtype=torch.bool),float("-inf"))
    weights = scores.softmax(dim=-1)
    return {"y":weights@v,"weights":weights}
''',[{key:value for key,value in c.items() if key not in ('eps','scale')} for c in [ATTN_CASES[0],dict(ATTN_CASES[2]),dict(q=[[[1,2]], [[-1,0]]],k=[[[2,0]], [[1,-1]]],v=[[[1,2]], [[3,4]]],mask=[[[1]], [[1]]])]],complexity='O(B*S²*(D+Dv)) 时间，O(B*S²) 权重空间。',doc='generated/torch.nn.functional.scaled_dot_product_attention.html',explanation='掩码必须在 softmax 前施加，之后每行权重和为 1。若在 softmax 之后清零而不重新归一化，会错误改变 y 的尺度。')
add(4034,'QK-Norm Attention','q：[B,Sq,D]、k：[B,Sk,D]、v：[B,Sk,Dv]；eps>0、scale>0。先分别执行 q_norm=q/max(||q||2,eps)、k_norm=k/max(||k||2,eps)，然后 scores=scale*q_norm@k_norm^T，weights=softmax(scores,dim=-1)，y=weights@v。本题无掩码、不再除以 sqrt(D)，零向量归一化仍为零。','返回 {y:[B,Sq,Dv],weights:[B,Sq,Sk]}。','''def solve(data):
    q,k,v = [T(data[key]) for key in ("q","k","v")]
    q = q/q.norm(dim=-1,keepdim=True).clamp_min(data["eps"])
    k = k/k.norm(dim=-1,keepdim=True).clamp_min(data["eps"])
    weights = (data["scale"]*(q@k.transpose(-2,-1))).softmax(dim=-1)
    return {"y":weights@v,"weights":weights}
''',[{key:value for key,value in c.items() if key!='mask'} for c in ATTN_CASES],complexity='O(B*Sq*Sk*(D+Dv)) 时间，O(B*Sq*Sk) 空间。',doc='generated/torch.nn.functional.normalize.html',difficulty='困难',explanation='在向量范数上 clamp 最小值，与 sqrt(sum(q²)+eps) 不同。归一化后再乘显式 scale 控制 softmax 温度。')


def values(shape, offset=0, scale=0.2):
    """Hand-defined deterministic pattern, independent of all RNG state."""
    n = math.prod(shape)
    return ((((torch.arange(n,dtype=torch.float64)+offset)%11)-5)*scale).reshape(shape).tolist()


RES_CASES = []
for b,c,h,w,offset in [(1,1,3,3,0),(2,2,2,3,2),(1,2,1,2,5)]:
    RES_CASES.append(dict(x=values([b,c,h,w],offset),w1=values([c,c,3,3],offset+1,0.07),b1=values([c],offset+3,0.1),w2=values([c,c,3,3],offset+4,0.05),b2=values([c],offset+6,0.1)))
add(1643,'Residual Block','x：[B,C,H,W]；w1、w2：[C,C,3,3]；b1、b2：[C]。两次卷积均 stride=1、padding=1，无 BatchNorm：z=ReLU(conv2d(x,w1,b1))，y=ReLU(x+conv2d(z,w2,b2))。','返回形状 [B,C,H,W] 的残差块输出。','''def solve(data):
    x = T(data["x"])
    z = F.relu(F.conv2d(x,T(data["w1"]),T(data["b1"]),padding=1))
    return F.relu(x+F.conv2d(z,T(data["w2"]),T(data["b2"]),padding=1))
''',RES_CASES,complexity='O(B*H*W*C²*9) 时间，O(B*C*H*W) 激活空间。',doc='generated/torch.nn.Conv2d.html',explanation='跳连必须加到第二层卷积输出上，最后再激活；只在第一层后激活与在残差相加后激活有不同效果。')

add(3693,'前馈网络前向计算','x：[B,D]，w1：[H,D]、b1：[H]、w2：[O,H]、b2：[O]。采用输出通道在前的权重布局；hidden=ReLU(x@w1^T+b1)，logits=hidden@w2^T+b2；不施加 softmax。','返回 {hidden:[B,H],logits:[B,O]}。','''def solve(data):
    hidden = F.relu(T(data["x"])@T(data["w1"]).T+T(data["b1"]))
    return {"hidden":hidden,"logits":hidden@T(data["w2"]).T+T(data["b2"])}
''',[dict(x=values([b,d],off),w1=values([h,d],off+2),b1=values([h],off+4),w2=values([o,h],off+5),b2=values([o],off+7)) for b,d,h,o,off in [(2,3,4,2,0),(1,2,1,3,2),(3,1,2,1,5)]],complexity='O(B*(D*H+H*O)) 时间，O(B*(H+O)) 空间。',doc='generated/torch.nn.Linear.html')
add(3694,'线性全连接层反向传播求导','x：[B,D]、weight：[O,D]、bias：[O]；dy：[B,O] 是损失对 y=x@weight^T+bias 的上游梯度。计算 dx=dy@weight，dweight=dy^T@x，dbias=sum_batch(dy)，不取平均。','返回 {dx:[B,D],dweight:[O,D],dbias:[O]}。','''def solve(data):
    x,w,dy = [T(data[k]) for k in ("x","weight","dy")]
    return {"dx":dy@w,"dweight":dy.T@x,"dbias":dy.sum(0)}
''',[dict(x=values([b,d],off),weight=values([o,d],off+2),bias=values([o],off+4),dy=values([b,o],off+5)) for b,d,o,off in [(2,3,2,0),(1,2,3,2),(3,1,1,5)]],complexity='O(B*D*O) 时间，O(B*D+O*D+O) 输出空间。',doc='generated/torch.nn.Linear.html')

# Contrastive losses deliberately differ in normalization, mining and reduction.
add(3941,'InfoNCE','anchor、positive：[B,D]，B≥2；每行非零，temperature>0。先逐行 L2 归一化；scores[i,j]=cos(anchor[i],positive[j])/temperature。每行的同索引 positive 为唯一正例，其余为负例；返回单向 batch 平均 CE，不进行对称化。','返回标量 InfoNCE 损失。','''def solve(data):
    a,p = [F.normalize(T(data[k]),dim=-1) for k in ("anchor","positive")]
    scores = a@p.T/data["temperature"]
    return (torch.logsumexp(scores,dim=1)-scores.diag()).mean()
''',[dict(anchor=[[1,0],[0,1],[-1,1]],positive=[[1,1],[0,2],[-1,0]],temperature=0.2),dict(anchor=[[1,2],[2,-1]],positive=[[-1,2],[2,1]],temperature=0.7),dict(anchor=[[1,1,0],[0,1,1],[1,0,1]],positive=[[2,1,0],[0,2,1],[1,0,2]],temperature=0.03)],complexity='O(B²*D) 时间，O(B²) 空间。',doc='generated/torch.nn.functional.normalize.html',difficulty='困难')
add(3942,'Triplet Loss','anchor、positive、negative：[B,D]；margin≥0。本题使用平方欧氏距离（不取平方根，不归一化）：L[i]=max(||a-p||²-||a-n||²+margin,0)，然后对 B 个样本取平均。','返回 {per_sample:[B],loss:标量}。','''def solve(data):
    a,p,n = [T(data[k]) for k in ("anchor","positive","negative")]
    loss = ((a-p).square().sum(-1)-(a-n).square().sum(-1)+data["margin"]).clamp_min(0)
    return {"per_sample":loss,"loss":loss.mean()}
''',[dict(anchor=[[0,0],[1,1]],positive=[[1,0],[1,2]],negative=[[2,0],[1,1.5]],margin=1),dict(anchor=[[1,-1]],positive=[[2,-1]],negative=[[1,-1]],margin=0.2),dict(anchor=[[0,0,0],[1,2,3],[2,1,0]],positive=[[0,0,1],[1,2,3],[2,0,0]],negative=[[0,2,0],[1,2,2],[2,2,0]],margin=0.5)],complexity='O(B*D) 时间，O(B) 损失空间。',doc='generated/torch.nn.TripletMarginLoss.html')
add(3943,'Circle Loss','sp、sn：非空正对/负对余弦相似度数组，元素∈[-1,1]；margin∈(0,1)，gamma>0。ap=max(1+margin-sp,0)，an=max(sn+margin,0)；lp=-gamma*ap*(sp-(1-margin))，ln=gamma*an*(sn-margin)；L=softplus(logsumexp(lp)+logsumexp(ln))。本题只评估前向标量，不计算梯度。','返回一个 Circle Loss 标量，不对正负对数量取平均。','''def solve(data):
    sp,sn = T(data["sp"]),T(data["sn"])
    m,g = data["margin"],data["gamma"]
    lp = -g*(1+m-sp).clamp_min(0)*(sp-(1-m))
    ln = g*(sn+m).clamp_min(0)*(sn-m)
    return F.softplus(torch.logsumexp(lp,0)+torch.logsumexp(ln,0),threshold=30)
''',[dict(sp=[0.9,0.6],sn=[0.3,-0.4,0.1],margin=0.25,gamma=32),dict(sp=[-0.8],sn=[0.95],margin=0.1,gamma=256),dict(sp=[1,0.98,0.95],sn=[-1,-0.6],margin=0.3,gamma=64)],complexity='O(P+N) 时间与空间。',doc='generated/torch.logsumexp.html',difficulty='困难',explanation='先在对数域分别汇总正负项，再用稳定 softplus 合并，避免 exp 在较大的 gamma 下溢出或溢出。')
add(3944,'CoSENT Loss','scores：[N] 相似度，labels：[N] 相关性等级（可重复），scale>0。取所有 labels[i]>labels[j] 的有序对，z=scale*(scores[j]-scores[i])；L=log(1+sum(exp(z)))。若没有严格等级对，L=0。','返回一个标量排序损失；相同标签的样本对完全忽略。','''def solve(data):
    scores,labels = T(data["scores"]),T(data["labels"])
    z = data["scale"]*(scores[None,:]-scores[:,None])
    selected = z[labels[:,None]>labels[None,:]]
    return torch.logsumexp(torch.cat((torch.zeros(1,dtype=torch.float64),selected)),0)
''',[dict(scores=[0.8,0.3,0.5,0.2],labels=[2,1,2,0],scale=20),dict(scores=[-0.8,0.9,0.1],labels=[3,1,2],scale=1000),dict(scores=[0.1,0.2,0.3],labels=[1,1,1],scale=10)],complexity='O(N²) 时间与空间。',doc='generated/torch.logsumexp.html',difficulty='困难')

# Recurrent cell fixtures have varied batch/time/hidden sizes and nonzero initial states.
SEQ_CASES = []
for b,t,d,h,off in [(1,3,2,2,0),(2,2,1,3,2),(1,1,3,1,5)]:
    SEQ_CASES.append(dict(x=values([b,t,d],off,0.3),h0=values([b,h],off+1,0.1),c0=values([b,h],off+2,0.2),w_ih=values([4*h,d],off+3,0.12),w_hh=values([4*h,h],off+5,0.08),bias=values([4*h],off+7,0.1)))
add(4031,'LSTM 序列前向传播','x：[B,T,D]，h0、c0：[B,H]；w_ih：[4H,D]，w_hh：[4H,H]，bias：[4H]。按时间顺序 a=x_t@w_ih^T+h_prev@w_hh^T+bias，沿最后一轴分成 i,f,g,o；i、f、o 用 sigmoid，g 用 tanh；c=f*c_prev+i*g，h=o*tanh(c)。只有一层，无 dropout。','返回 {output:[B,T,H],h:[B,H],c:[B,H]}；T=1 时也保留时间轴。','''def solve(data):
    x,h,c,wi,wh,b = [T(data[k]) for k in ("x","h0","c0","w_ih","w_hh","bias")]
    output = []
    for xt in x.unbind(dim=1):
        i,f,g,o = (xt@wi.T+h@wh.T+b).chunk(4,dim=-1)
        c = f.sigmoid()*c+i.sigmoid()*g.tanh()
        h = o.sigmoid()*c.tanh()
        output.append(h)
    return {"output":torch.stack(output,dim=1),"h":h,"c":c}
''',SEQ_CASES,complexity='O(B*T*H*(D+H)) 时间，O(B*T*H) 输出/激活空间。',doc='generated/torch.nn.LSTM.html',difficulty='困难',explanation='每个时间步使用上一步 h、c，并注意四组门的排列 i,f,g,o。不能把整个时间轴当作互不相关的批量线性层。')

RNN_CASES=[]
for b,t,d,h,off in [(1,3,2,2,0),(2,2,1,3,2),(1,1,3,1,5)]:
    RNN_CASES.append(dict(x=values([b,t,d],off,0.3),h0=values([b,h],off+1,0.1),w_ih=values([h,d],off+3,0.12),w_hh=values([h,h],off+5,0.08),bias=values([h],off+7,0.1)))
add(4032,'SimpleRNN 与 BPTT','x：[B,T,D]；h0：[B,H]；w_ih：[H,D]、w_hh：[H,H]、bias：[H]。递推 h_t=tanh(x_t@w_ih^T+h_prev@w_hh^T+bias)。L=1/2*sum_{b,t,h}(h_t²)，包含全部时间步，不做平均。通过完整 BPTT 求导（不得截断/分离历史状态），允许 autograd。','返回 {output:[B,T,H],loss:标量,dx:[B,T,D],dh0:[B,H],dw_ih:[H,D],dw_hh:[H,H],dbias:[H]}。','''def solve(data):
    x,h0,wi,wh,b = [T(data[k]).requires_grad_() for k in ("x","h0","w_ih","w_hh","bias")]
    h = h0
    seq = []
    for xt in x.unbind(1):
        h = torch.tanh(xt@wi.T+h@wh.T+b)
        seq.append(h)
    out = torch.stack(seq,1)
    loss = out.square().sum()/2
    dx,dh0,dwi,dwh,db = torch.autograd.grad(loss,(x,h0,wi,wh,b))
    return {"output":out,"loss":loss,"dx":dx,"dh0":dh0,"dw_ih":dwi,"dw_hh":dwh,"dbias":db}
''',RNN_CASES,complexity='O(B*T*H*(D+H)) 前后向时间；O(B*T*(H+D)+H*(D+H)) 空间。',doc='generated/torch.nn.RNN.html',difficulty='困难',explanation='所有时间步共享权重；前面隐藏状态对后续损失的影响必须反向传播。对全部 output 的平方和一次性求导可自然累加这些路径。')

GRU_CASES=[]
for b,d,h,off in [(2,2,2,0),(1,1,3,3),(1,3,1,6)]:
    GRU_CASES.append(dict(x=values([b,d],off,0.3),h=values([b,h],off+1,0.2),w_ih=values([3*h,d],off+3,0.1),w_hh=values([3*h,h],off+5,0.08),b_ih=values([3*h],off+6,0.1),b_hh=values([3*h],off+8,0.1)))
add(4033,'GRU Cell','x：[B,D]，h：[B,H]，w_ih：[3H,D]，w_hh：[3H,H]，b_ih、b_hh：[3H]。按 r,z,n 顺序分组 input=x@w_ih^T+b_ih、hidden=h@w_hh^T+b_hh；r=sigmoid(input_r+hidden_r)，z=sigmoid(input_z+hidden_z)，n=tanh(input_n+r*hidden_n)，h_new=(1-z)*n+z*h。重置门作用在 hidden_n（含其偏置）之后，采用 PyTorch 约定。','返回形状 [B,H] 的新隐藏状态。','''def solve(data):
    x,h,wi,wh,bi,bh = [T(data[k]) for k in ("x","h","w_ih","w_hh","b_ih","b_hh")]
    ir,iz,inn = (x@wi.T+bi).chunk(3,-1)
    hr,hz,hn = (h@wh.T+bh).chunk(3,-1)
    r,z = (ir+hr).sigmoid(),(iz+hz).sigmoid()
    n = (inn+r*hn).tanh()
    return (1-z)*n+z*h
''',GRU_CASES,complexity='O(B*H*(D+H)) 时间，O(B*H) 额外空间。',doc='generated/torch.nn.GRUCell.html',difficulty='困难')

DENSE_CASES=[]
for b,c,h,w,growth,layers,off in [(2,2,2,3,1,2,0),(1,1,3,2,2,1,3),(1,2,1,2,1,3,6)]:
    DENSE_CASES.append(dict(x=values([b,c,h,w],off,0.3),weights=[values([growth,c+growth*l,3,3],off+l*2,0.06) for l in range(layers)],biases=[values([growth],off+l+1,0.03) for l in range(layers)],eps=1e-4))
add(5565,'DenseNet Block','x：[B,C,H,W]；weights：L 个卷积核，第 l 个核形状 [G,C+l*G,3,3]；biases：L 个 [G] 数组；eps>0。每层对当前所有通道沿 (B,H,W) 做无仿射 BatchNorm（总体方差、训练态、无 running state），再 ReLU，再 padding=1 的 conv2d，产生 G 个新通道并拼接到当前张量末尾。下一层可见所有历史通道。','返回形状 [B,C+L*G,H,W] 的最终拼接特征。','''def solve(data):
    x = T(data["x"])
    for weight,bias in zip(data["weights"],data["biases"]):
        z = (x-x.mean((0,2,3),keepdim=True))/torch.sqrt(x.var((0,2,3),unbiased=False,keepdim=True)+data["eps"])
        new = F.conv2d(F.relu(z),T(weight),T(bias),padding=1)
        x = torch.cat((x,new),dim=1)
    return x
''',DENSE_CASES,complexity='O(B*H*W*9*G*sum_l(C+l*G)) 时间，O(B*H*W*(C+L*G)) 特征空间。',doc='generated/torch.cat.html',difficulty='困难',explanation='DenseNet 使用沿通道拼接而不是相加；每层卷积输入通道数随层数增长。这里省去瓶颈层，但保留 BN-ReLU-Conv 和密集连接的核心结构。')

add(5570,'AMP GradScaler Step','param、scaled_grad：相同形状；scale>0、lr>0；found_inf：显式溢出标志（JSON 不传 Inf/NaN）；growth_tracker≥0，growth_interval≥1，growth_factor>1，backoff_factor∈(0,1)。未溢出时 grad=scaled_grad/scale，param_new=param-lr*grad，tracker 加一，到 growth_interval 时 scale 乘 growth_factor 且 tracker 归零。溢出时跳过参数更新，scale 乘 backoff_factor，tracker 归零。此题只模拟缩放器状态机，不要求 GPU 或自动混合精度内核。','返回 {param:新参数,scale:新缩放因子,growth_tracker:整数,stepped:布尔}。','''def solve(data):
    p = T(data["param"])
    scale,tracker = data["scale"],data["growth_tracker"]
    if data["found_inf"]:
        return {"param":p,"scale":scale*data["backoff_factor"],"growth_tracker":0,"stepped":False}
    p = p-data["lr"]*T(data["scaled_grad"])/scale
    tracker += 1
    if tracker >= data["growth_interval"]:
        scale *= data["growth_factor"]
        tracker = 0
    return {"param":p,"scale":scale,"growth_tracker":tracker,"stepped":True}
''',[dict(param=[[1,-2]],scaled_grad=[[16,-8]],scale=8,lr=0.1,found_inf=False,growth_tracker=0,growth_interval=2,growth_factor=2,backoff_factor=0.5),dict(param=[1,2,-1],scaled_grad=[400,0,-200],scale=100,lr=0.03,found_inf=False,growth_tracker=2,growth_interval=3,growth_factor=2,backoff_factor=0.25),dict(param=[[[2],[-1]]],scaled_grad=[[[0],[0]]],scale=32,lr=0.2,found_inf=True,growth_tracker=1,growth_interval=2,growth_factor=2,backoff_factor=0.5)],doc='amp.html',difficulty='困难',explanation='梯度必须先除以旧 scale 再更新参数；增长后的 scale 用于下次迭代。溢出路径不读取梯度并跳过整个 optimizer step。')

CHECKPOINT_CASES=[]
for b,d,h,o,off in [(2,3,4,2,0),(1,2,2,1,3),(3,1,3,2,5)]:
    CHECKPOINT_CASES.append(dict(x=values([b,d],off,0.3),w1=values([h,d],off+2,0.12),b1=values([h],off+4,0.1),w2=values([o,h],off+5,0.1),b2=values([o],off+7,0.05),target=values([b,o],off+8,0.2)))
add(5571,'Activation Checkpointing','x：[B,D]；w1：[H,D]、b1：[H]、w2：[O,H]、b2：[O]；target：[B,O]。y=tanh(x@w1^T+b1)@w2^T+b2，loss=mean((y-target)^2)。必须把 tanh 线性块放入 torch.utils.checkpoint.checkpoint(...,use_reentrant=False)，反向时重计算，求全部输入与参数梯度。评测数值等价性；节省内存的实现要求由代码审查核对，单纯输出无法证明是否使用 checkpoint。','返回 {y:[B,O],loss:标量,dx:[B,D],dw1:[H,D],db1:[H],dw2:[O,H],db2:[O]}。','''def solve(data):
    from torch.utils.checkpoint import checkpoint
    x,w1,b1,w2,b2 = [T(data[k]).requires_grad_() for k in ("x","w1","b1","w2","b2")]
    def block(a,weight,bias):
        return torch.tanh(a@weight.T+bias)
    hidden = checkpoint(block,x,w1,b1,use_reentrant=False)
    y = hidden@w2.T+b2
    loss = (y-T(data["target"])).square().mean()
    grads = torch.autograd.grad(loss,(x,w1,b1,w2,b2))
    return dict(zip(("y","loss","dx","dw1","db1","dw2","db2"),(y,loss,*grads)))
''',CHECKPOINT_CASES,complexity='时间 O(B*(D*H+H*O))，checkpoint 额外重算一次块；块内部激活不需全部保存，返回值与梯度仍占用相应输出空间。',doc='checkpoint.html',difficulty='困难',explanation='checkpoint 在反向阶段重新执行块，节约内部激活的保存成本。use_reentrant=False 可搭配 autograd.grad；目标和参数均保持 float64，便于检验与普通前向的梯度一致。')

GAN_CASES=[]
for b,z,d,off in [(2,2,2,0),(3,1,2,3),(1,2,1,6)]:
    GAN_CASES.append(dict(real=values([b,d],off,0.4),noise=values([b,z],off+1,0.3),gw=values([d,z],off+2,0.12),gb=values([d],off+3,0.1),dw=values([1,d],off+4,0.16),db=values([1],off+5,0.1),lr_d=0.05,lr_g=0.03))
add(5572,'GAN Training Step','real：[B,D]，noise：[B,Z]；生成器 G(z)=tanh(z@gw^T+gb)，gw：[D,Z]、gb：[D]；判别器 logits D(x)=x@dw^T+db，dw：[1,D]、db：[1]；lr_d、lr_g>0。先以 detached fake 做判别器 SGD：Ld=mean(softplus(-D(real)))+mean(softplus(D(fake)))（两项之和，不除以 2）。更新 D 后，固定新 D，使用相同 noise 重新计算 G，Lg=mean(softplus(-D_new(G(noise))))，再更新 G。无动量、无衰减。','返回 {gw,gb,dw,db:本轮新参数,loss_d:更新 D 前的标量损失,loss_g:更新 D 后且更新 G 前的标量损失}。','''def solve(data):
    real,z = T(data["real"]),T(data["noise"])
    gw,gb,dw,db = [T(data[k]).requires_grad_() for k in ("gw","gb","dw","db")]
    fake = torch.tanh(z@gw.T+gb).detach()
    ld = F.softplus(-(real@dw.T+db)).mean()+F.softplus(fake@dw.T+db).mean()
    ddw,ddb = torch.autograd.grad(ld,(dw,db))
    dw_new = (dw-data["lr_d"]*ddw).detach()
    db_new = (db-data["lr_d"]*ddb).detach()
    new_fake = torch.tanh(z@gw.T+gb)
    lg = F.softplus(-(new_fake@dw_new.T+db_new)).mean()
    dgw,dgb = torch.autograd.grad(lg,(gw,gb))
    return {"gw":gw-data["lr_g"]*dgw,"gb":gb-data["lr_g"]*dgb,"dw":dw_new,"db":db_new,"loss_d":ld,"loss_g":lg}
''',GAN_CASES,complexity='O(B*D*Z) 前后向时间，O(B*(D+Z)+D*Z) 空间。',doc='generated/torch.nn.BCEWithLogitsLoss.html',difficulty='困难',explanation='判别器更新时 fake 必须 detach；生成器损失使用已经更新的 D。采用 non-saturating 生成器损失，并用 softplus 避免 sigmoid 后再 log 的精度问题。')

add(5573,'VAE ELBO Loss','logits、target：[B,D]，target∈[0,1]；mu、logvar、epsilon：[B,Z]；beta≥0。重参数化 z=mu+exp(logvar/2)*epsilon。重建项 recon[i]=sum_d(BCEWithLogits(logits[i,d],target[i,d]))；kl[i]=-1/2*sum_z(1+logvar-mu²-exp(logvar))；loss=mean(recon+beta*kl)。epsilon 为给定确定性噪声，不再采样；返回的是负 ELBO。','返回 {z:[B,Z],reconstruction:[B],kl:[B],loss:标量}。','''def solve(data):
    logits,target,mu,lv,eps = [T(data[k]) for k in ("logits","target","mu","logvar","epsilon")]
    z = mu+torch.exp(lv/2)*eps
    recon = F.binary_cross_entropy_with_logits(logits,target,reduction="none").sum(-1)
    kl = -0.5*(1+lv-mu.square()-lv.exp()).sum(-1)
    return {"z":z,"reconstruction":recon,"kl":kl,"loss":(recon+data["beta"]*kl).mean()}
''',[dict(logits=[[2,-1,0],[-3,1,4]],target=[[1,0,1],[0,1,1]],mu=[[0.2,-0.3],[1,0]],logvar=[[0,0.5],[-1,0.2]],epsilon=[[1,-1],[0.5,2]],beta=1),dict(logits=[[1000,-1000]],target=[[1,0]],mu=[[0]],logvar=[[0]],epsilon=[[2]],beta=0.3),dict(logits=[[0,1],[-1,2],[3,-2]],target=[[0.2,0.8],[1,0],[0.5,1]],mu=[[1,2],[0,-1],[0.2,-0.3]],logvar=[[-0.5,0.2],[0,0],[-2,1]],epsilon=[[0,1],[-1,0.5],[2,-0.2]],beta=0)],complexity='O(B*(D+Z)) 时间与空间。',doc='generated/torch.nn.BCEWithLogitsLoss.html',difficulty='困难')

add(5574,'DDPM Forward Process','x0、noise：相同形状 [B,...]，至少二维；betas：[T] 且每项∈(0,1)；timesteps：[B]，从 0 开始（0 已执行第一次加噪）。alpha_bar[t]=prod_{s=0..t}(1-betas[s])；每个样本 xt=sqrt(alpha_bar[t])*x0+sqrt(1-alpha_bar[t])*noise。噪声由输入给定，不再采样。','返回 {xt:与 x0 同形,alpha_bar:[B]}，alpha_bar 按 timesteps 索引而非返回整条调度。','''def solve(data):
    x,noise = T(data["x0"]),T(data["noise"])
    schedule = (1-T(data["betas"])).cumprod(0)
    selected = schedule[torch.tensor(data["timesteps"],dtype=torch.long)]
    a = selected.reshape(x.shape[0],*([1]*(x.ndim-1)))
    return {"xt":a.sqrt()*x+(1-a).sqrt()*noise,"alpha_bar":selected}
''',[dict(x0=[[1,-1],[2,0]],noise=[[0.2,0.5],[-1,2]],betas=[0.1,0.2,0.3],timesteps=[0,2]),dict(x0=[[[[1,2],[3,4]]]],noise=[[[[-1,0],[1,2]]]],betas=[0.001,0.005,0.01,0.02],timesteps=[3]),dict(x0=[[[1],[2]],[[3],[4]],[[5],[6]]],noise=[[[0],[1]],[[-1],[0.5]],[[2],[-2]]],betas=[0.4,0.6],timesteps=[1,0,1])],complexity='O(T+N) 时间，O(T+B) 调度空间和 O(N) 输出空间，N 为 x0 元素数。',doc='generated/torch.cumprod.html',difficulty='困难',explanation='闭式前向扩散使用累计 alpha_bar 而非单步 alpha。为每个样本选取时间步后，需要在所有特征/空间轴广播，避免批次轴与通道轴混淆。')

CONV3_CASES=[]
for b,ci,co,d,h,w,k,groups,off in [(1,1,2,3,3,3,2,1,0),(1,2,2,2,2,3,1,2,3),(2,1,1,3,2,2,2,1,5)]:
    CONV3_CASES.append(dict(x=values([b,ci,d,h,w],off,0.3),w=values([co,ci//groups,k,k,k],off+2,0.08),b=values([co],off+4,0.1),stride=[1,1,2] if off==3 else [1,1,1],padding=[1,0,1] if off==5 else [0,0,0],dilation=[1,1,1],groups=groups))
add(5575,'Conv3D Forward','x：[B,Cin,D,H,W]；w：[Cout,Cin/groups,Kd,Kh,Kw]；b：[Cout]；stride、padding、dilation：长度 3 的整数数组；groups 整除 Cin 和 Cout。执行不翻转核的 3D 互相关，零填充、floor 输出模式。','返回形状 [B,Cout,Dout,Hout,Wout] 的卷积结果。','''def solve(data):
    return F.conv3d(T(data["x"]),T(data["w"]),T(data["b"]),stride=data["stride"],padding=data["padding"],dilation=data["dilation"],groups=data["groups"])
''',CONV3_CASES,complexity='O(B*Cout*Dout*Hout*Wout*(Cin/groups)*Kd*Kh*Kw) 时间，O(输出元素数) 空间。',doc='generated/torch.nn.Conv3d.html',difficulty='困难')


def json_value(value):
    if isinstance(value, torch.Tensor):
        return value.detach().cpu().tolist()
    if isinstance(value, dict):
        return {k: json_value(v) for k,v in value.items()}
    if isinstance(value, (list,tuple)):
        return [json_value(v) for v in value]
    return value


def evaluate(entry, data):
    scope = {}
    exec(PRELUDE+'\n'+entry['code'],scope)
    return json_value(scope['solve'](copy.deepcopy(data)))


def build_catalog():
    result = []
    for e in ENTRIES:
        fixtures = [dict(input=json.dumps(c,ensure_ascii=False,allow_nan=False),expected=json.dumps(evaluate(e,c),ensure_ascii=False,allow_nan=False),hidden=i>0,compare='float_tokens',absTolerance=1e-6,relTolerance=1e-6) for i,c in enumerate(e['cases'])]
        contract = e['contract']
        result.append(dict(
            title=e['title']+'（原创练习）',category='深度学习',difficulty=e['difficulty'],tags=['原创练习','PyTorch',e['title']],
            description='本题是 CodeAce 根据公开数学定义独立编写的原创练习，未转载第三方题面。\n\n实现函数 `solve(data)`；data 是已解析的 Python dict，返回值为张量、数值或题目指定的对象。无需读取输入或打印，评测包装器自动序列化。\n\n'+contract+'\n\n'+e['output']+'\n\n所有浮点运算在 CPU 上进行，建议使用 torch.float64。评测逐层比较 JSON 结构与数组长度，并使用绝对/相对误差 1e-6；不得扁平化张量或删除长度为 1 的轴。',
            inputDescription='函数参数 data 为 JSON 对应字典。\n'+contract,
            outputDescription=e['output']+' 返回 Tensor 会由包装器转换成嵌套列表；对象键名必须完全匹配。',
            constraints='所有数组非空、规则、形状合法，输入为有限实数；维度大小不超过 32，单个数组元素数不超过 32768。其他范围以字段契约为准；正整数参数保证输出尺寸合法。仅支持 Python3 / PyTorch CPU，无需 CUDA 或网络。',
            hint=e['explanation'],
            solution='### 思路\n\n'+e['explanation']+'\n\n### 可运行参考实现\n\n以下代码可直接作为函数模式提交，辅助函数包含在内。\n\n```python\n'+PRELUDE+'\n'+e['code']+'```\n\n### 复杂度\n\n'+e['complexity']+'\n\n### 数值与接口约定\n\n'+e['output']+' 使用 float64；比较器在保留 JSON 嵌套形状的前提下容许 1e-6 绝对/相对误差。',
            source='codeace-original',sourceId=str(e['id']),sourceUrl='https://docs.pytorch.org/docs/stable/'+e['doc'],published=True,timeMs=10000,memoryMb=1024,
            modes=dict(function=dict(templates=dict(python3='def solve(data):\n    # data 字段、返回值形状和数学约定详见题面。\n    raise NotImplementedError\n'),prelude=PRELUDE,harness=HARNESS,cases=fixtures,inputHelp='JSON 字典。'+contract,runtime='torch')),
            samples=[dict(input=fixtures[0]['input'],output=fixtures[0]['expected'],explanation='展示用例；其余用例包含不同形状、非零状态或边界情况。')],
        ))
    return result


def assert_close(actual, expected, label='', atol=1e-8, rtol=1e-8):
    """Shape-aware comparison; does not accidentally broadcast differently shaped arrays."""
    if isinstance(expected,dict):
        assert set(actual)==set(expected),(label,'keys',actual,expected)
        for k in expected:
            assert_close(actual[k],expected[k],label+'/'+k,atol,rtol)
    elif isinstance(expected,(list,tuple)):
        assert isinstance(actual,(list,tuple)) and len(actual)==len(expected),(label,'shape')
        for i,(a,b) in enumerate(zip(actual,expected)):
            assert_close(a,b,label+f'/{i}',atol,rtol)
    elif isinstance(expected,bool):
        assert actual is expected,(label,actual,expected)
    else:
        assert math.isfinite(actual) and math.isclose(actual,expected,abs_tol=atol,rel_tol=rtol),(label,actual,expected)


def slow_conv(data, spatial):
    """Independent index-loop correlation oracle, including groups/dilation/padding."""
    import itertools
    x,w,b = [torch.tensor(data[k],dtype=torch.float64) for k in ('x','w','b')]
    stride,padding,dilation,groups = [data[k] for k in ('stride','padding','dilation','groups')]
    shape = [(x.shape[2+i]+2*padding[i]-dilation[i]*(w.shape[2+i]-1)-1)//stride[i]+1 for i in range(spatial)]
    out = torch.empty(x.shape[0],w.shape[0],*shape,dtype=torch.float64)
    out_per_group = w.shape[0]//groups
    for batch in range(x.shape[0]):
        for oc in range(w.shape[0]):
            first = (oc//out_per_group)*w.shape[1]
            for dest in itertools.product(*(range(n) for n in shape)):
                total = float(b[oc])
                for ic in range(w.shape[1]):
                    for kernel in itertools.product(*(range(n) for n in w.shape[2:])):
                        src = tuple(dest[i]*stride[i]-padding[i]+kernel[i]*dilation[i] for i in range(spatial))
                        if all(0<=src[i]<x.shape[2+i] for i in range(spatial)):
                            total += float(x[(batch,first+ic,*src)]*w[(oc,ic,*kernel)])
                out[(batch,oc,*dest)] = total
    return out


def independent_checks():
    """Library cross-checks, analytic GAN gradients and numerical derivative oracles."""
    by_id = {e['id']:e for e in ENTRIES}
    checks = 0
    def run(id,data):
        return evaluate(by_id[id],data)
    # LSTM and GRU gate order/reset placement checked against PyTorch modules.
    for data in SEQ_CASES:
        wi,wh = torch.tensor(data['w_ih']),torch.tensor(data['w_hh'])
        h = wh.shape[1]
        model = torch.nn.LSTM(wi.shape[1],h,batch_first=True,dtype=torch.float64)
        with torch.no_grad():
            model.weight_ih_l0.copy_(wi); model.weight_hh_l0.copy_(wh)
            model.bias_ih_l0.copy_(torch.tensor(data['bias'])); model.bias_hh_l0.zero_()
        out,(hn,cn)=model(torch.tensor(data['x']),(torch.tensor(data['h0'])[None],torch.tensor(data['c0'])[None]))
        assert_close(run(4031,data),json_value(dict(output=out,h=hn[0],c=cn[0])),'LSTM')
        checks += 1
    for data in GRU_CASES:
        h = len(data['h'][0]); d = len(data['x'][0])
        model=torch.nn.GRUCell(d,h,dtype=torch.float64)
        with torch.no_grad():
            for key in ('weight_ih','weight_hh','bias_ih','bias_hh'):
                source={'weight_ih':'w_ih','weight_hh':'w_hh','bias_ih':'b_ih','bias_hh':'b_hh'}[key]
                getattr(model,key).copy_(torch.tensor(data[source]))
        assert_close(run(4033,data),json_value(model(torch.tensor(data['x']),torch.tensor(data['h']))),'GRU')
        checks += 1
    # Full RNN BPTT checked against the fused torch.nn.RNN, including nonzero h0.
    for data in RNN_CASES:
        h,d=len(data['h0'][0]),len(data['x'][0][0])
        model=torch.nn.RNN(d,h,batch_first=True,dtype=torch.float64)
        with torch.no_grad():
            model.weight_ih_l0.copy_(torch.tensor(data['w_ih']));model.weight_hh_l0.copy_(torch.tensor(data['w_hh']))
            model.bias_ih_l0.copy_(torch.tensor(data['bias']));model.bias_hh_l0.zero_()
        x=torch.tensor(data['x'],requires_grad=True);h0=torch.tensor(data['h0'],requires_grad=True)
        out,_=model(x,h0[None]);loss=out.square().sum()/2
        grads=torch.autograd.grad(loss,(x,h0,model.weight_ih_l0,model.weight_hh_l0,model.bias_ih_l0))
        exp=dict(zip(('output','loss','dx','dh0','dw_ih','dw_hh','dbias'),(out,loss,*grads)))
        assert_close(run(4032,data),json_value(exp),'RNN BPTT')
        checks += 1
    # Independent index-loop convolution oracle; backward verified by finite differences.
    for data in CONV_CASES:
        assert_close(run(1630,data),json_value(slow_conv(data,2)),'Conv2D index oracle')
        got=run(5566,data)
        for field,gradient in [('x','dx'),('w','dw'),('b','db')]:
            base=torch.tensor(data[field],dtype=torch.float64);numerical=torch.empty_like(base)
            for i in range(base.numel()):
                plus,minus=copy.deepcopy(data),copy.deepcopy(data)
                xp,xm=base.clone(),base.clone();xp.view(-1)[i]+=1e-5;xm.view(-1)[i]-=1e-5
                plus[field],minus[field]=xp.tolist(),xm.tolist()
                numerical.view(-1)[i]=(slow_conv(plus,2).square().sum()-slow_conv(minus,2).square().sum())/(4e-5)
            assert_close(got[gradient],json_value(numerical),'Conv2D finite difference '+field,atol=1e-5,rtol=1e-5)
        checks += 4
    for data in CONV3_CASES:
        assert_close(run(5575,data),json_value(slow_conv(data,3)),'Conv3D index oracle')
        checks += 1
    # Hand-derived two-stage GAN gradients catch stale-D and wrong reduction mistakes.
    for data in GAN_CASES:
        real,z,gw,gb,dw,db=[torch.tensor(data[k]) for k in ('real','noise','gw','gb','dw','db')]
        fake=torch.tanh(z@gw.T+gb);B=real.shape[0]
        real_logit=real@dw.T+db;fake_logit=fake@dw.T+db
        gr=(real_logit.sigmoid()-1)/B;gf=fake_logit.sigmoid()/B
        new_dw=dw-data['lr_d']*(gr.T@real+gf.T@fake)
        new_db=db-data['lr_d']*(gr+gf).sum(0)
        gen_logit=fake@new_dw.T+new_db
        delta=((gen_logit.sigmoid()-1)@new_dw)*(1-fake.square())/B
        exp=dict(gw=gw-data['lr_g']*(delta.T@z),gb=gb-data['lr_g']*delta.sum(0),dw=new_dw,db=new_db,loss_d=torch.logaddexp(torch.zeros_like(real_logit),-real_logit).mean()+torch.logaddexp(torch.zeros_like(fake_logit),fake_logit).mean(),loss_g=torch.logaddexp(torch.zeros_like(gen_logit),-gen_logit).mean())
        assert_close(run(5572,data),json_value(exp),'GAN analytic SGD')
        checks += 1
    # Ordinary autograd must match the checkpointed graph exactly.
    for data in CHECKPOINT_CASES:
        args=[torch.tensor(data[k],requires_grad=True) for k in ('x','w1','b1','w2','b2')]
        x,w1,b1,w2,b2=args
        y=torch.tanh(x@w1.T+b1)@w2.T+b2;loss=(y-torch.tensor(data['target'])).square().mean()
        grads=torch.autograd.grad(loss,args)
        assert_close(run(5571,data),json_value(dict(zip(('y','loss','dx','dw1','db1','dw2','db2'),(y,loss,*grads)))),'checkpoint equivalence')
        checks += 1
    # Adam state checked against the optimizer implementation (nonzero historical moments).
    for data in OPT_CASES:
        param=torch.nn.Parameter(torch.tensor(data['param']))
        optimizer=torch.optim.Adam([param],lr=data['lr'],betas=(data['beta1'],data['beta2']),eps=data['eps'])
        optimizer.state[param]=dict(step=torch.tensor(float(data['step']-1)),exp_avg=torch.tensor(data['m']),exp_avg_sq=torch.tensor(data['v']))
        param.grad=torch.tensor(data['grad']);optimizer.step()
        state=optimizer.state[param]
        assert_close(run(1646,data),json_value(dict(param=param,m=state['exp_avg'],v=state['exp_avg_sq'])),'Adam torch optimizer')
        checks += 1
    # Dense concat checked using independent BatchNorm module dispatch.
    for data in DENSE_CASES:
        x=torch.tensor(data['x'])
        for weight,bias in zip(data['weights'],data['biases']):
            bn=torch.nn.BatchNorm2d(x.shape[1],eps=data['eps'],affine=False,track_running_stats=False,dtype=torch.float64)
            feature=F.conv2d(F.relu(bn(x)),torch.tensor(weight),torch.tensor(bias),padding=1)
            x=torch.cat([x,feature],1)
        assert_close(run(5565,data),json_value(x),'DenseNet batchnorm oracle')
        checks += 1
    # DDPM scalar product loop checks per-example time indexing/broadcasting.
    for data in by_id[5574]['cases']:
        alpha=[];acc=1.
        for beta in data['betas']:
            acc*=1-beta;alpha.append(acc)
        got=run(5574,data)
        for b,t in enumerate(data['timesteps']):
            expected=math.sqrt(alpha[t])*torch.tensor(data['x0'][b])+math.sqrt(1-alpha[t])*torch.tensor(data['noise'][b])
            assert_close(got['xt'][b],json_value(expected),'DDPM scalar oracle')
            assert_close(got['alpha_bar'][b],alpha[t],'DDPM schedule')
        checks += 1
    # Forward invariants cover stable softmax, exact masking and losses.
    for id,axis in [(1623,1),(3705,1),(3718,0)]:
        for data in by_id[id]['cases']:
            out=torch.tensor(run(id,data))
            assert torch.allclose(out.sum(axis),torch.ones_like(out.sum(axis)))
            assert (out>=0).all() and torch.isfinite(out).all()
            checks += 1
    for data in by_id[1626]['cases']:
        out=run(1626,data);weight=torch.tensor(out['weights']);mask=torch.tensor(data['mask'])
        assert (weight[mask==0]==0).all()
        assert torch.allclose(weight.sum(-1),torch.ones_like(weight.sum(-1)))
        checks += 1
    return checks


def verify_catalog(catalog):
    import io
    import contextlib
    import sys
    assert len(catalog)==65 and len({p['sourceId'] for p in catalog})==65
    assert len({e['id'] for e in ENTRIES})==65
    runs=0
    for problem in catalog:
        variant=problem['modes']['function']
        # Execute the actual published Markdown reference and harness, not a separate callback.
        solution=problem['solution'].split('```python\n',1)[1].split('```',1)[0]
        for case in variant['cases']:
            capture=io.StringIO();old_stdin=sys.stdin
            try:
                sys.stdin=io.StringIO(case['input'])
                with contextlib.redirect_stdout(capture):
                    exec(variant['prelude']+'\n'+solution+'\n'+variant['harness'],{})
            finally:
                sys.stdin=old_stdin
            actual=json.loads(capture.getvalue())
            assert_close(actual,json.loads(case['expected']),problem['sourceId'],1e-6,1e-6)
            runs+=1
    independent=independent_checks()
    print(f'Validated {len(catalog)} original exercises; {runs} published reference+harness cases; {independent} independent mathematical/library checks.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true',help='Regenerate database/deep-catalog.json after validation')
    args=parser.parse_args()
    catalog=build_catalog()
    verify_catalog(catalog)
    path=ROOT/'database/deep-catalog.json'
    if args.write:
        path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
        print(f'Wrote {path}')
    else:
        saved=json.loads(path.read_text())
        assert saved==catalog,'Saved catalog differs from authored references; regenerate with --write'
        print('Saved catalog matches trusted references exactly.')
