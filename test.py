score = int(input("請輸入成績："))
if score >= 60:
    print("及格")
else:
    print("不及格")

num = int(input("請輸入一個數："))
for i in range(num+1):
    if i % 2:
        print(i)

num = input("請輸入學號：")
print(num[0:2])

num_list = []
for i in range(6):
    num_list.append(int(input("請依序輸入第"+str(i+1)+"個數字：")))
for i in range(6):
    if num_list[i] > 5:
        print(num_list[i])

num = int(input("請輸入正方形邊長："))
def GetArea(x):
    return x*x
print(GetArea(num))