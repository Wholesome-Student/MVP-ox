def qr_encode(id:str|int,ans:bool) -> int:
    return int(id)*2+(1 if ans else 0)

def qr_decode(data:str|bytes) -> dict:
    try:
        if type(data)==bytes:
            data=data.decode()
        num=int(data)
        return {"id":"%03d"%(num//2),"ans":num%2==1}
    except:
        return {"id":"","ans":None}

def checksum(num:int):
    num=abs(num)
    sum=0
    while num>0:
        sum+=num%10
        num//=10
    return sum%10