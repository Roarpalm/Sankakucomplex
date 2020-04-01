import os, time

os.system('git add -A')
time.sleep(1)
os.system("git commit -m ''")
time.sleep(2)
os.system('git push -u origin master')