import json
import os
def get_number(str):
   Info= os.popen("curl -G %s"%(str)).read()    
   json_r=json.loads(Info)
   j=0
   for i in json_r:
     j=j+1
   return j
   
   
#get_number('https://api.github.com/repos/defunkt/starling/contributors')