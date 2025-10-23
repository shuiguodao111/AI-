
import os
pyfile_path=os.path.dirname(os.path.abspath(__file__))

exec(open(pyfile_path+'/src/f00_prepare.py').read())
exec(open(pyfile_path+'/src/f01_load.py').read())
exec(open(pyfile_path+'/src/f02_write.py').read())
exec(open(pyfile_path+'/src/f03_util.py').read())
exec(open(pyfile_path+'/src/f04_run.py').read())


################################
def main():
    bkg_messages=loadBKG()
    tmp_messages=loadTMP()
    new_messages=loadNEW_kimi(sys.argv[1:])
    #new_messages=loadNEW(sys.argv[1:])
    new_messages=checkNewMessage(new_messages)
    all_messages=bkg_messages+tmp_messages+new_messages
    result=getResult(all_messages)
    #result=getResult_ollama(all_messages) 
    this_tmp_content=getTMP(new_messages, result)
    #print(this_tmp_content)
    if(TMP_USE==True):
        writeTMP(this_tmp_content)
    if(LOG_USE==True):
        writeLOG(this_tmp_content)





