import sqlite3
import wrapper

connection=sqlite3.connect('./stocktrading.db')
cur=connection.cursor()

flag=0
flag2=0
while(flag==0):
	print("")
	option=int(input("WELCOME TO STOCK TRADING GAME\n\nEnter any of the below options:\n1 - Create a new User\n2 - Existing User? Login HERE\n3 - Delete User\n4 - Update Password\n5 - ADMIN LOGIN\n6 - Exit\n"))
	if(option==1):
		id1=input("Enter User ID:\n")
		pwd=input("Enter Password\n")
		name=input("Enter your first name:\n")
		wallet=100000
		cur.execute(''' INSERT INTO users VALUES(?,?,?,?);''',[id1,pwd,name,wallet])
		print("New User sucessfully created - $100,000 has been added to your balance\n")
	elif(option==2):
		id1=input("Enter User ID:\n")
		pwd=input("Enter Password\n")
		cur.execute('''SELECT username FROM users''')
		row=cur.fetchall()
		cur.execute('''SELECT password FROM users''')
		row2=cur.fetchall()
		testuser=str(row)
		testpwd=str(row2)
		if id1 in testuser:
			if pwd in testpwd:
				while(flag2==0):
					print("DASHBOARD OF USER: ",id1,"\n")
					opt=int(input("CLICK THE BELOW OPTIONS TO CONTINUE\n1-Search Stocks by company name\n2-Update and View Existing Stocks\n3-Buy Stocks\n4-Sell Stocks\n5-Exit\n"))
					if(opt==1):
						try:
							m = wrapper.Markit()
							name = input('Enter the Company Name\n')
							name = name.upper()
							print(name)
							formal_name, ticker_symbol, exchange = m.company_search(name)
							print("formal name: ", formal_name)
							print("ticker symbol: ", ticker_symbol)
							print("exchnage: ", exchange)
							last_price = m.get_quote(ticker_symbol)
							print("last stock price: ", last_price)
						except:
							print("Error - API has been called too many times or Wrong Input - Try again after sometime")
					elif(opt==2):
						# cur.execute('''SELECT company WHERE USERNAME=?;''' [id1])

						cur.execute('''SELECT company FROM stocks WHERE user=?;''', [id1])
						temp=cur.fetchall()

						a=[]
						b=[]
						for i in range(len(temp)):
							a.append(temp[i][0])

						lena=len(a)

						try:
							for i in range(lena):
							
								m = wrapper.Markit()
								formal_name, ticker_symbol, exchange = m.company_search(a[i])
								last_price = m.get_quote(ticker_symbol)
								b.append(last_price)


							newsum=0

							cur.execute('''SELECT qty FROM stocks WHERE user=?;''',[id1])
							temp2=cur.fetchall()
						
							quant=[]
							for i in range(lena):
								quant.append(temp2[i][0])

							cur.execute('''SELECT curvalue FROM stocks WHERE user=?;''',[id1])
							temp3=cur.fetchall()
						
							oldprice=[]
							for i in range(lena):
								oldprice.append(temp3[i][0])


							for i in range(lena):
								cur.execute('''UPDATE stocks SET curvalue=? WHERE company=? and user=?;''',[b[i],a[i],id1])
								newsum=newsum+((b[i]-oldprice[i])*quant[i])
								connection.commit()

							cur.execute('''SELECT wallet FROM users WHERE username=?;''',[id1])
							temp=cur.fetchall()
							bal=temp[0][0]
							bal=bal+newsum

						#need to write code to update wallet/balance
							cur.execute('''UPDATE users SET wallet=? WHERE username=?;''',[bal,id1])


							cur.execute('''SELECT wallet FROM users WHERE username=?;''',[id1])
							temp=cur.fetchall()
							bal=temp[0][0]
							print("\nYour current balance is $",bal,"\n")
							print("Your portfolio is as below:\n")
							cur.execute(''' SELECT type,company,value,curvalue,qty FROM stocks WHERE user=?;''',[id1])
							temp=cur.fetchall()
							l=len(temp)
							print("LAST TRANSACTION | COMPANY | BUY PRICE | CURRENT VALUE | QUANTITY OWNED")
							for i in range(l):
								for j in range(5):
									print(temp[i][j],end="   ")
								print("\n")
						
						except:
							print("Error - API has been called too many times or Wrong Input - Try again after sometime")		

					elif(opt==3):
						cur.execute('''SELECT wallet FROM users WHERE username=?;''',[id1])
						temp=cur.fetchall()
						bal=temp[0][0]
						print("\nYour current balance is $",bal,"\n")
						
						try:

							m = wrapper.Markit()
							name = input('Enter the Company Name\n')
							name=name.upper()
							sname, tckr, xchng = m.company_search(name)
							last_price = m.get_quote(tckr)
							print(sname,"(",tckr,") in ",xchng,"exchange is priced at: ",last_price,"\n")
							q=int(input("Enter number of stocks to be bought:\n"))

						
								
							totval=last_price*q
							if totval<bal:
								newbal=bal-totval
								cur.execute('''SELECT company FROM stocks WHERE user=?;''', [id1])
								temp=cur.fetchall()
								listofcomp=[]
								for i in range(len(temp)):
									listofcomp.append(temp[i][0])

								# print("\n",listofcomp,"\n")

								if name in listofcomp:

									cur.execute('''SELECT qty FROM stocks WHERE company=? and user=?''',[name,id1])
									tempquant=cur.fetchall()

									# print("\n",q,"\n")
									# print("\n",tempquant,"\n")

									q=q+tempquant[0][0]

									# print(q)

									cur.execute(''' UPDATE stocks SET type=?, qty=?, curvalue=? WHERE user=? AND company=?;''',['buy',q,last_price,id1,name])
									cur.execute(''' UPDATE users SET wallet=? WHERE username=?;''',[newbal,id1])
									print(sname," was successfully bought. Your remaining balance is: $",newbal," and new stock quantity is ",q,"\n")
							
								else:
									cur.execute(''' INSERT INTO stocks VALUES(?,?,?,?,?,?);''',['buy',id1,name,last_price,q,last_price])
									cur.execute(''' UPDATE users SET wallet=? WHERE username=?;''',[newbal,id1])
									print(sname," was successfully bought. Your remaining balance is: $",newbal,"\n")
									connection.commit()
						
							else:
								print("Insufficient balance. Try again.\n")
						except:
							print("Error - API has been called too many times or Wrong Input - Try again after sometime")

					elif(opt==4):
						print("Your current stocks are as below:\n")
						print("STOCK NAME    |    VALUE    |    QUANTITY")
						cur.execute(''' SELECT company,value,qty FROM stocks WHERE user=?;''',[id1])
						temp=cur.fetchall()
						l=len(temp)
						comptemp=[]
						for i in range(l):
							comptemp.append(temp[i][0])
							for j in range(3):
								print(temp[i][j],end="   ")
							print("\n")
						cur.execute('''SELECT wallet FROM users WHERE username=?;''',[id1])
						temp=cur.fetchall()
						bal=temp[0][0]
						print("\nYour current balance is $",bal,"\n")

						try:
							m = wrapper.Markit()
							loopflag=0
							while loopflag==0:
								name = input('Enter the Company Name of the Stock to be sold\n')
								name=name.upper()
								if name in comptemp:
									loopflag=1
								else:
									print("wrong stock name entered - try again")
							
							sname, tckr, xchng = m.company_search(name)
							last_price = m.get_quote(tckr)
							name=name.upper()
						except:
							print("Error - API has been called too many times or Wrong Input - Try again after sometime")

						print(sname,"(",tckr,") in ",xchng,"exchange is priced at: ",last_price,"\n")
						q=int(input("Enter number of stocks to be sold:\n"))
						cur.execute(''' SELECT company,value,qty FROM stocks WHERE user=? AND company=?;''',[id1,name])
						container=cur.fetchall()
						comp=container[0][0]
						val=container[0][1]
						qt=container[0][2]
						if(comp==name):
							if(qt>=q):
								# print(comp,val,qt,"sucessfully updated")
								newq=qt-q
								totval=q*last_price
								newbal=bal+totval
								cur.execute('''UPDATE stocks set qty=?, curvalue=?, type=? WHERE company=?''', [newq,last_price,'sell',name])
								cur.execute('''UPDATE users set wallet=? WHERE username=?''', [newbal,id1])
								print(q," no of stocks were successfully sold at $",last_price," per stock\nYour new balance is ",newbal)
							else:
								print("Number of Stocks to be sold cannot be greater than number of stocks owned\n")
						else:
							print(name," stock not owned")

					else:
						flag2=1
			else:
				print("Wrong Password Entered - Try Again")
		else:
			print("Username Does Not Exist")

	elif(option==3):
		temp=input("Enter User ID to be deleted\n")
		pwd=input("Enter Password\n")
		cur.execute('''SELECT username FROM users''')
		row=cur.fetchall()
		cur.execute('''SELECT password FROM users''')
		row2=cur.fetchall()
		testuser=str(row)
		testpwd=str(row2)
		if temp in testuser:
			if pwd in testpwd:
				cur.execute('''DELETE FROM users WHERE username=?;''',[temp])
				cur.execute('''DELETE FROM stocks WHERE user=?;''',[temp])
				connection.commit()
				print("User successfully deleted")
			else:
				print("Wrong Password Entered")
		else:
			print("User ID does not exist")

	elif(option==4):
		temp=input("Enter User ID who's password needs to be updated:\n")
		pwd=input("Enter Password\n")
		cur.execute('''SELECT username FROM users''')
		row=cur.fetchall()
		cur.execute('''SELECT password FROM users''')
		row2=cur.fetchall()
		testuser=str(row)
		testpwd=str(row2)
		if temp in testuser:
			if pwd in testpwd:
				newpwd=input("Enter New Password\n")
				cur.execute('''UPDATE users set password=? WHERE username=?''', [newpwd, temp])
				print("Password successfully updated")
			else:
				print("Wrong Password Entered")
		else:
			print("User ID does not exist")

	elif(option==5):
		adminflag=0
		u='admin'
		p='admin'
		a1=input("\nEnter ADMIN Username\n")
		a2=input("Enter ADMIN Password\n")
		if(u==a1 and p==a2):
			while adminflag==0:
				print("\nWELCOME ADMINISTRATOR\n")
				option=int(input("Enter the below options to continue\n1-View all user info\n2-View Detailed User Info\n3-Add user\n4-Remove user\n5-Exit\n"))
				if(option==1):
					cur.execute('''SELECT name,wallet,username,password FROM users''')
					temp=cur.fetchall()
					print("NAME  |  BALANCE($)  |  LOGIN NAME  |  PASSWORD")
					for i in range(len(temp)):
						for j in range(4):
							print(temp[i][j],end="    ")
						print("\n")

				elif(option==3):
					id1=input("Enter User ID:\n")
					pwd=input("Enter Password\n")
					name=input("Enter your first name:\n")
					wallet=100000
					cur.execute(''' INSERT INTO users VALUES(?,?,?,?);''',[id1,pwd,name,wallet])
					print("New User sucessfully created - $100,000 has been added to",name,"'s balance\n")

				elif(option==4):
					temp=input("Enter User ID to be deleted\n")
					pwd=input("Are you Sure? Enter (Y) to continue\n")
					pwd=pwd.upper()
					cur.execute('''SELECT username FROM users''')
					row=cur.fetchall()
					testuser=str(row)
					if temp in testuser:
						if pwd=='Y':
							cur.execute('''DELETE FROM users WHERE username=?;''',[temp])
							cur.execute('''DELETE FROM stocks WHERE user=?;''',[temp])
							connection.commit()
							print("User successfully deleted")
						else:
							print("Wrong Input Entered")
					else:
						print("User ID does not exist")

				elif(option==2):
					print("\nThe list of users is as below\n")
					cur.execute('''SELECT username FROM users''')
					temp=cur.fetchall()	
					namelist=[]
					for i in range(len(temp)):
						print(i+1,". ",temp[i][0])
						namelist.append(temp[i][0])

					name=input("\nEnter the name of the user who's details are to be viewed\n")
					if name in namelist:
						cur.execute('''SELECT company, type, qty, curvalue, value FROM stocks WHERE user=?;''',[name])
						temp2=cur.fetchall()
						print("STOCK NAME | LAST TRANSACTION | QUANTITY | CURRENT VALUE | BUY VALUE")
						for i in range(len(temp2)):
							for j in range(5):
								print(temp2[i][j],end='           ')
							print("\n")

					else:
						print("Wrong name entered")

				else:
					adminflag=1
		else:
			print("Wrong Credentials Entered")

	else:
		print("Exiting....")
		flag=1




connection.commit()
connection.close()