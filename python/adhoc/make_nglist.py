#不正ログインを検出しリスト化する

import subprocess
from subprocess import PIPE
from collections import Counter

proc = subprocess.run("lastb -i | head --lines=-2 | awk '{print $3}'", shell=True, stdout=PIPE, stderr=PIPE, text=True)

ip_list = proc.stdout.split("\n")
#ipアドレスの頻度
ip_count = Counter(ip_list)
#不正なフォーマットを削除かつ10以上のログインエラーでngリスト
ng_list = [k for k, v in ip_count.items() if len(k.split("."))==4 and v > 10]

with open('nglist.txt', 'w') as f:
    for ngip in ng_list:
        f.write(f"{ngip}\n")

#その後nglistをfire-wallで登録する
#例
#初回時のみ実行
#firewall-cmd --permanent --new-ipset=nglist --type=hash:net
#都度実行
#firewall-cmd --permanent --ipset=nglist --add-entries-from-file=nglist.txt
#firewall-cmd --reload
