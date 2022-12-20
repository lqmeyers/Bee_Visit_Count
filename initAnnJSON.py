import json
import datetime

init = {'Init':{'Datetime':str(datetime.datetime.now())},'Photos':{}} 

with open('annotated.json','w')as f:
    json.dump(init,f,indent=2)