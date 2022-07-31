import requests
from bs4 import BeautifulSoup as BS
import tkinter as tk
import tkinter.messagebox as mb
import webbrowser

VERSION = "0.0.6"

def callback():
	webbrowser.open_new("https://pubmed.ncbi.nlm.nih.gov/")


def click_button_insert():
	input_field.delete(0, tk.END)
	input_field.insert(0, root.clipboard_get())
	print(root.clipboard_get())


def click_button_search():
	global link
	link = input_field.get()
	output_field.delete("1.0", tk.END)
	pubmed_parsing(link)
	output_field.insert("1.0", result)
	if complex_names_of_authors:
		show_info()


def click_button_copy():
	root.clipboard_clear()
	root.clipboard_append(output_field.get("1.0", tk.END))
	root.update()


def click_button_write():
	f = open('output.txt', 'a', encoding="utf-8")
	f.write(result + "\n\n")
	f.close()


def show_info():
	if len(complex_names_of_authors) == 1:
		msg = "Статья содержит сложное имя автора:\n"
	elif len(complex_names_of_authors) > 1:
		msg = "Статья содержит сложные имена авторов: \n"

	for el in complex_names_of_authors:
		msg += el +"\n"

	if len(complex_names_of_authors) == 1:
		msg += "Отредактируйте его вручную"
	elif len(complex_names_of_authors) > 1:
		msg += "Отредактируйте их вручную"

	mb.showinfo("Информация", msg)


def pubmed_parsing(link):
	global complex_names_of_authors
	complex_names_of_authors = []

	try:
		r = requests.get(link)
		soup = BS(r.content, 'html.parser')

		journal = soup.find("button", id="full-view-journal-trigger")
		#print(journal.text)
		journal = journal.text.strip()

		data = soup.select(".cit")
		#print(data[0].text)
		data = data[0].text.strip()

		title = soup.select(".heading-title")
		#print(title[0].text)
		title = title[0].text.strip()

		atrs = []
		for el in soup.select(".authors-list > .authors-list-item"):
			authors = el.select(".full-name")
			#print(authors[0].text)
			atrs.append(authors[0].text)
		del atrs[int((len(atrs)-1)/2):(len(atrs))] #костыль
		#print (atrs)

		spases = 0
		abbreviated_author = ""
		counter = 0
		atrs_index = 0
		index = 0
		bool_a = True
		for element in atrs:
			for i in element:
				if i == " ":
					spases +=1

			if spases == 1:
				abbreviated_author += element[0] + "."
				for j in element:
					if j == " ":
						counter +=1
					if counter == 1:
						abbreviated_author += j

				counter = 0
				atrs[atrs_index] = abbreviated_author
				atrs_index += 1
				#print(element)
				abbreviated_author = ""

			if spases == 2:
				abbreviated_author += element[0] + "."
				for j in element:
					if j == " ":
						counter +=1
					if counter == 1 and bool_a:
						abbreviated_author += atrs[atrs_index][index+1] + "."
						bool_a = False
					if counter == 2:
						abbreviated_author += j
					index += 1

				index = 0
				counter = 0
				bool_a = True
				atrs[atrs_index] = abbreviated_author
				atrs_index += 1
				#print(element)
				abbreviated_author = ""

			if spases > 2:
				complex_names_of_authors.append(atrs[atrs_index])
				atrs_index += 1

			spases = 0

		#print (atrs)


		first_author = ""
		initials = ""
		bool_b = True
		for element in atrs[0]:
			if element == " ":
				bool_b = False
			if element != " " and bool_b:
				initials += element
			if not bool_b:
				first_author +=element
		first_author += ", " + initials + " "
		bool_b = True

		#print(first_author)


		new_data = ""
		for i in range(4):
			new_data += data[i]
		new_data += ". – V. "


		bool_c = False
		for i in range(len(data)):
			if data[i] == ":":
				bool_c = False
			if bool_c:
				new_data += data[i]
			if data[i] == ";":
				bool_c = True

		new_data += ". – P. "

		for i in range(len(data)):
			if bool_c:
				new_data += data[i]
			if data[i] == ":":
				bool_c = True
		bool_c = False


		new_journal = ""
		for i in range(len(journal)):
			if journal[i] != " ":
				new_journal += journal[i]
			else:
				new_journal += ". "


		global result
		result = ""
		result += first_author
		result += title + " / "

		for i in range(len(atrs)):
			result += atrs[i]
			if i+1 != len(atrs):
				result += ", "
			else:
				result += " // "
		result += new_journal + ". – "
		result += new_data

	except:
		result = "ОШИБКА. Неверно введена ссылка"




root = tk.Tk()
root.title("Оформление литературы по ГОСТу ЮФУ")
#root.minsize(500,500)
root.resizable(width=False, height=False)

opts = { 'ipadx': 4, 'ipady': 4 , 'sticky': 'nswe', 'padx': 10, 'pady': 10 }

description = tk.Label(text="Программа создает готовую для списка литеруры строку, \nиспользуя ссылку на статью с сайта pubmed. \nНайдите на этом сайте статью и вставьте ссылку на нее ниже ")
description.grid(row=0, column=0, columnspan=2)

btn_link = tk.Button(text="Перейти на сайт https://pubmed.ncbi.nlm.nih.gov/", width=16, command=callback)
btn_link.grid(row=1, column=0, columnspan=2, **opts)

enter_the_link = tk.Label(text="Введите ссылку на статью с pubmed: ")
enter_the_link.grid(row=2, column=0, columnspan=2)

input_field = tk.Entry(fg="black", bg="white", width=60)
input_field.grid(row=3, column=0, columnspan=2)

btn_insert = tk.Button(text="Вставить", width=16, command=click_button_insert)
btn_insert.grid(row=4, column=0, **opts)

btn_search = tk.Button(text="Сгенерировать", width=16, command=click_button_search)
btn_search.grid(row=4, column=1, **opts)

output_field = tk.Text(fg="black", bg="white", width=50, height=12)
output_field.grid(row=5, column=0, columnspan=2, padx=10)

btn_copy = tk.Button(text="Скопировать", command=click_button_copy)
btn_copy.grid(row=6, column=0, **opts)

btn_write = tk.Button(text="Записать в output.txt", command=click_button_write)
btn_write.grid(row=6, column=1, **opts)

creator = tk.Label(text="Made by Vladimir Partko", fg="blue")
creator.grid(row=7, column=0, columnspan=2)

version = tk.Label(text=VERSION, fg="black")
version.grid(row=8, column=0, columnspan=2)

root.mainloop()

