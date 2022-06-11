import gspread
import pandas as pd

file_name = hoge
sheet_id =  fuga
sheet_name = piyo

#gspread用のインスタンスを立ち上げる
gc = gspread.service_account(filename=file_name)
#spread sheetを選択。sheet_idはspread sheetの第三階層
#https://docs.google.com/spreadsheets/d/の後の部分)
#例:https://docs.google.com/spreadsheets/d/hogehogehoge/edit?hl=JA#gid=0
#↑hogehogehogeがsheet_id
sh = gc.open_by_key(sheet_id)
#シートを選択。sheet_nameはシートタブ名
worksheet = sh.worksheet(sheet_name)
#シートのデータをDataframe方式で出力
sheet_df = pd.DataFrame(worksheet.get_all_records(head=1))

#出力
#>>> sheet_df
#   sample
#0       1
