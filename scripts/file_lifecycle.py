import os
import time
import shutil
import traceback
from pprint import pprint
from datetime import datetime

path = '/data/var/openebs/local/pvc-71c9dc93-1d09-4632-abaf-7ab4cb16ee86/result'

try:
    current_time = time.time()
    for folder in os.listdir(path):
        folder_path = os.path.join(path, folder)
        if os.path.isdir(folder_path):
            modified_time = os.path.getmtime(folder_path)
            fmt = datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d %H:%M:%S")
            age = current_time - modified_time
            if age > 7 * 24 * 60 * 60:
                try:
                    pprint(folder_path + 'modified time:' + fmt)
                    # shutil.rmtree(folder_path)
                    pprint('deleting:' + folder_path)
                except OSError as e:
                    pprint("can not delete : " + folder_path + 'erro:' + e)
except Exception as e:
    pprint(traceback.format_exc())
