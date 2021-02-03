import json, urllib3
import qa_appinfo as QAInfo

url = QAInfo.version_check_url
http = urllib3.PoolManager()

def check() -> bool:
    try:
        REQ = http.request('GET', url)
    except:
        return True
    
    __data = REQ.data.decode().encode('utf-8')
    __dict = json.loads(__data)
    
    print(f"<<%%{__dict}%%>>")
    
    __vers = __dict['version']
    __tolSub = __dict['tolerateSub']
    
    __curr = QAInfo.versionData.get(
        QAInfo.VFKeys.get('v')
    )
    
    print(__tolSub)
    
    if not __tolSub:
        if type(__curr) is type(__vers):
            
            print(f'<<1:1:{__curr}/{__vers}::{int(__curr == __vers)}>>')
            return __curr == __vers

        else: 
            print(f"<<1:2:0>>")
            return False
    
    else:
        __curr = str(__curr).split('.')[0].strip()
        __vers = str(__vers).split('.')[0].strip()
        
        print(f"<<2:{__curr}/{__vers}::{int(__curr == __vers)}>>")
        
        return __curr == __vers
