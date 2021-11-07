import tkinter as tk
from tkinter import *
from tkinter import messagebox
import pymysql
from datetime import datetime
import re


class TodoListGUI:
    def __init__(self, tk_obj):
        self.tk_obj = tk_obj
        self.tk_obj.title('ToDo_List')
        self.tk_obj.geometry('700x420')
        # GUI Title
        self.label_1 = Label(self.tk_obj, text="Organize Your Work & Life",
                             font='ariel, 24 bold', width=700, bd=5, bg='#40e0d0', fg='black')
        self.label_1.pack(side='top', fill=BOTH)
        # "Manage Task" title
        self.label_2 = Label(self.tk_obj, text="Manage Task",
                             font='ariel, 20 bold', width=14, bd=8, fg='black')
        self.label_2.place(x=0, y=70)
        # "Tasks List" title
        self.label_3 = Label(self.tk_obj, text="Tasks List",
                             font='ariel, 20 bold', width=10, bd=8, fg='black')
        self.label_3.place(x=405, y=70)
        # "Tasks list" window
        self.scrollbar = tk.Scrollbar(self.tk_obj)
        self.scrollbar.pack(side="right", fill=BOTH)
        self.taskList = Listbox(self.tk_obj, height=10, bd=2, width=38, bg='#fafad2',
                                font='ariel, 15 italic bold', yscrollcommand=self.scrollbar.set)
        self.taskList.place(x=260, y=120)
        # Enter task text
        self.text = Text(self.tk_obj, height=4, bd=2, width=30, font='ariel, 10 bold')
        self.text.place(x=20, y=120)

        def __conn_mysql():
            conn = pymysql.connect(
                host='localhost', port=3306,
                user='testuser', passwd='qwe123456',  # Change user & passwd
                db='todo_list'
                )
            cursor = conn.cursor()
            return conn, cursor

        def __close_conn(conn, cursor):
            conn.commit()
            cursor.close()
            conn.close()

        def add():
            add_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            taksContent = self.text.get(1.0, END).replace('\n', '').capitalize()
            print(f'Add task = {taksContent}')
            self.taskList.insert(END, taksContent)

            # Insert record to db
            conn, cursor = __conn_mysql()
            sql = 'INSERT INTO task_data VALUES(%s, %s, %s);'
            cursor.execute(sql, (taksContent.lower(), add_time, None))  # lower for formatting
            __close_conn(conn, cursor)
            self.text.delete(1.0, END)

        def clean_timedelta(coat_time):
            day = coat_time.days
            hour = coat_time.seconds // 3600
            minute = (coat_time.seconds - (3600 * hour)) // 60
            second = coat_time.seconds - (3600 * hour) - (60 * minute)
            return f'Total cost = {day}days, {hour}hours, {minute}minutes, {second}seconds'

        def delete():
            del_time = datetime.now()
            deleteTask = self.taskList.curselection()
            for index in deleteTask[::-1]:
                taskContent = self.taskList.get(index).replace('\n', '').lower()  # lower for formatting
                self.taskList.delete(index)
                print(f'Delete task = {taskContent}')

            # Select add_time from db to count coat_time
            conn, cursor = __conn_mysql()
            sql_query = f'SELECT add_time FROM task_data WHERE task = "{taskContent}";'
            cursor.execute(sql_query)
            print(cursor.fetchall()[0][0])
            # cost_time = clean_timedelta((del_time - cursor.fetchall()[0][0]))
            # tk.messagebox.showinfo(title='Cost time', message=cost_time)
            # print(f'Cost_time = {cost_time}')
            # Delete record from db
            sql_del = f'DELETE FROM task_data WHERE task = "{taskContent}";'
            cursor.execute(sql_del)
            __close_conn(conn, cursor)

        # Read exist tasks from db
        conn, cursor = __conn_mysql()
        cursor.execute('SELECT task FROM task_data;')
        for task in cursor.fetchall():
            self.taskList.insert(END, task[0].capitalize())
        __close_conn(conn, cursor)

        # "Add" button
        self.button = Button(self.tk_obj, text='Add', font='ariel, 20 bold',
                             width=10, bd=5, bg='orange', fg='white', command=add)
        self.button.place(x=37, y=220)
        # "Delete" button
        self.button = Button(self.tk_obj, text='Delete', font='ariel, 20 bold ',
                             width=10, bd=5, bg='orange', fg='white', command=delete)
        self.button.place(x=37, y=300)

def main():
    window = tk.Tk()
    TodoListGUI(window)
    window.mainloop()


if __name__ == '__main__':
    main()

