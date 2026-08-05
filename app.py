from tkinter import Tk, Label, Button, Entry, messagebox, Toplevel
from tkinter import ttk

from database import Database
from logger import logger
from manager import app, Book

def create_tree(parent, columns, headings, widths):
  tree = ttk.Treeview(
    parent,
    columns=columns,
    show="headings"
    )
    
  for column in columns:
    tree.heading(column, text=headings[column])
    tree.column(column, width=widths[column], stretch=True)
    
  return tree

class LibraryGUI:
  def __init__(self, root, app, db):
    self.root = root
    root.title("Library System")
    self.app = app
    self.db = db
    self.controller = Controller(self)
    
    self.title_label = Label(self.root, text="Welcome to Student Library Management System!")
    self.title_label.pack()
    
    self.status_label = Label(self.root, text="Ready")
    self.status_label.pack()
      
    self.notebook = ttk.Notebook(self.root)
    self.notebook.pack(fill="both", expand=True)
    
    self.library_tab = ttk.Frame(self.notebook)
    self.students_tab = ttk.Frame(self.notebook)
    self.logs_tab = ttk.Frame(self.notebook)
    
    self.notebook.add(self.library_tab, text="Library")
    self.notebook.add(self.students_tab, text="Student")
    self.notebook.add(self.logs_tab, text="Logs")
    
    self.library_frame = LibraryFrame(self)
    self.student_frame = StudentFrame(self)
    self.log_frame = LogFrame(self)
        
  def display_books(self, data):
    for item_id in self.library_frame.books_tree.get_children():
      self.library_frame.books_tree.delete(item_id)
      
    for info in data:
      self.library_frame.books_tree.insert(
        "",
        "end",
        values=(
          info['book_id'],
          info['title'],
          info['author'],
          info['year_published'],
          info['stock']
          )
        )
  
  def display_students(self, data):
    for item_id_row in self.student_frame.student_tree.get_children():
      self.student_frame.student_tree.delete(item_id_row)
      
    for info in data:
      self.student_frame.student_tree.insert(
        "",
        "end",
        values=(
          info['name'],
          info['title'],
          info['book_id'],
          info['quantity'],
          )
        )
        
  def display_logs(self, logs):
    for item_id in self.log_frame.logs_tree.get_children():
      self.log_frame.logs_tree.delete(item_id)
      
    for log in logs:
      self.log_frame.logs_tree.insert(
        "",
        "end",
        values=(
          log['action'],
          log['student'],
          log['book_id'],
          log['quantity'],
          log['timestamp'],
          )
        )
  
class Controller:
  def __init__(self, gui):
    self.gui = gui
    self.root = gui.root
    self.app = gui.app
    self.db = gui.db
    
  def add_book(self):
    window = Toplevel(self.root)
    window.title("Add Book")
    
    Label(window, text="Book ID (ex.B001)").pack()
    enter_id_entry = Entry(window)
    enter_id_entry.pack()
    
    Label(window, text="Title").pack()
    title_entry = Entry(window)
    title_entry.pack()
    
    Label(window, text="Author").pack()
    author_entry = Entry(window)
    author_entry.pack()
    
    Label(window, text="Year Published").pack()
    year_published_entry = Entry(window)
    year_published_entry.pack()
    
    Label(window, text="Stock").pack()
    stock_entry = Entry(window)
    stock_entry.pack()
    
    def save():
      enter_id = enter_id_entry.get()
        
      valid = self.gui.app.library.can_add_book(enter_id, self.db)
        
      if not valid['success']:
        logger.warning(f"ADD_BOOK_FAILED | REASON={valid['log_message']}")
        messagebox.showerror("Error", valid['message'])
        return
      
      title = title_entry.get()
        
      if not title:
        messagebox.showerror("Error", "Please enter a title.")
        return
      
      author = author_entry.get()
        
      if not author:
        messagebox.showerror("Error", "Please enter an author.")
        return
        
      try:
        year_published = int(year_published_entry.get())
      except ValueError:
        messagebox.showerror("Error", "Please enter only a number")
        return
        
      if year_published < 1000 or year_published > 9999:
        messagebox.showerror("Error", "Please enter a valid year.")
        return
        
      try:
        stock = int(stock_entry.get())
      except ValueError:
        messagebox.showerror("Error", "Please enter only a number.")
        return
        
      if stock < 0:
        messagebox.showerror("Error", "Please enter a valid number.")
        return
        
      book = Book(enter_id, title, author, year_published, stock)
      
      self.db.insert_book(book.b_id, book.title, book.author, book.year_published, book.stock)
      
      self.stored_books()
        
      logger.info("ADD_BOOK_SUCCESS")
      self.gui.status_label.config(text=valid['message'])
      
      self.db.commit()
        
      window.destroy()
        
    Button(window, text="Save", command=save).pack()
      
  def remove_book(self):
    window = Toplevel(self.root)
    window.title("Remove Book")
    
    Label(window, text="Book ID").pack()
    remove_book_entry = Entry(window)
    remove_book_entry.pack()
    
    def save():
      remove_book = remove_book_entry.get()
        
      valid = self.app.library.can_remove_book(remove_book, self.db)
        
      if not valid['success']:
        logger.warning(f"REMOVE_BOOK_FAILED | REASON={valid['log_message']}")
        messagebox.showerror("Error", valid['message'])
        return
      
      book = self.db.get_book(remove_book)
          
      confirm = messagebox.askyesno("Confirm Removal", f"\nAre you sure you want to remove '{book['title']}'?")
          
      if not confirm:
        self.gui.status_label.config(text="Removing cancelled!")
        return
      
      self.db.delete_book(remove_book)
        
      logger.info("REMOVE_BOOK_SUCCESS")
      self.gui.status_label.config(text=valid['message'])
      
      self.db.commit()
        
      window.destroy()
    
    Button(window, text="Save", command=save).pack()
    
  def borrow_book(self):
    window = Toplevel(self.root)
    window.title("Borrow Book")
    
    Label(window, text="Name").pack()
    name_entry = Entry(window)
    name_entry.pack()
    
    Label(window, text="Book ID").pack()
    enter_id_entry = Entry(window)
    enter_id_entry.pack()
    
    Label(window, text="Number of Books Borrowed").pack()
    num_books_borrowed_entry = Entry(window)
    num_books_borrowed_entry.pack()
    
    def save():
      name = name_entry.get()
        
      if not name:
        messagebox.showerror("Error", "Please enter a name.")
        return
      
      enter_book_id = enter_id_entry.get()
      
      try:
        num_books_borrowed = int(num_books_borrowed_entry.get())
      except ValueError:
        messagebox.showerror("Error", "Please enter only a number.")
        return
        
      if num_books_borrowed <= 0:
        messagebox.showerror("Error", "Please enter a valid number.")
        return
        
      valid = self.app.library.can_borrow(enter_book_id, num_books_borrowed, self.db)
        
      if not valid['success']:
        logger.warning(f"BORROW_BOOK_FAILED | REASON={valid['log_message']}")
        messagebox.showerror("Error", valid['message'])
        return
        
      self.app.borrowed.borrow_book(name, enter_book_id, num_books_borrowed, self.db)
        
      logger.info("BORROW_BOOK_SUCCESS")
      self.gui.status_label.config(text=valid['message'])
        
      self.db.log_action("BORROW", name, enter_book_id, num_books_borrowed)
      
      self.db.commit()
      
      window.destroy()
      
    Button(window, text="Save", command=save).pack()
        
  def return_book(self):
    window = Toplevel(self.root)
    window.title("Return Book")
    
    Label(window, text="Name").pack()
    name_entry = Entry(window)
    name_entry.pack()
    
    Label(window, text="Book ID").pack()
    enter_id_entry = Entry(window)
    enter_id_entry.pack()
    
    Label(window, text="Number of Books Returned").pack()
    num_books_returned_entry = Entry(window)
    num_books_returned_entry.pack()
    
    def save():
      name = name_entry.get()
        
      if not name:
        messagebox.showerror("Error", "Please enter a name.")
        return
        
      borrowed = self.app.borrowed.students_borrowed(name, self.db)
        
      if not borrowed['success']:
        self.gui.status_label.config(text="Student not found.")
        return
          
      enter_book_id = enter_id_entry.get()
      
      num_books_returned = int(num_books_returned_entry.get())
        
      if not num_books_returned:
        messagebox.showerror("Error", "Please enter only a number.")
        return
      
      if num_books_returned <= 0:
        messagebox.showerror("Error", "Please enter a valid number.")
        return
          
      valid = self.app.library.can_return(name, enter_book_id, num_books_returned, self.db)
          
      if not valid['success']:
        logger.warning(f"RETURN_BOOK_FAILED | REASON={valid['log_message']}")
        messagebox.showerror("Error", valid['message'])
        return
        
      self.app.library.return_book(name, enter_book_id, num_books_returned, self.db)
        
      logger.info("RETURN_BOOK_SUCCESS")
      self.gui.status_label.config(text=valid['message'])
        
      self.db.log_action("RETURN", name, enter_book_id, num_books_returned)
      
      self.db.commit()
        
      window.destroy()
      
    Button(window, text="Save", command=save).pack()
      
  def search_student(self):
    window = Toplevel(self.root)
    window.title("Search Student")
    
    Label(window, text="Name").pack()
    name_entry = Entry(window)
    name_entry.pack()
    
    def search():
      name = name_entry.get()
        
      if not name:
        messagebox.showerror("Error", "Please enter a name.")
        return
        
      valid = self.app.borrowed.search_student_filter(name, self.db)
        
      if not valid['success']:
        messagebox.showerror("Error", valid['message'])
        return
      
      self.gui.display_students(valid['message'])
      
      window.destroy()
      
    Button(window, text="Search", command=search).pack()
      
  def search_log_student(self):
    window = Toplevel(self.root)
    window.title("Search Log Student")
    
    Label(window, text="Name").pack()
    name_entry = Entry(window)
    name_entry.pack()
    
    def search():
      name = name_entry.get()
        
      if not name:
        messagebox.showerror("Error", "Please enter a name")
        return
        
      logs = self.db.get_log_student(name)
        
      if not logs:
        self.gui.status_label.config(text=f"There are no history with {name}")
        return
        
      self.gui.display_logs(logs)
      
      window.destroy()
      
    Button(window, text="Search", command=search).pack()
      
  def search_book(self):
    window = Toplevel(self.root)
    window.title("Search Book")
    
    Label(window, text="Title").pack()
    title_entry = Entry(window)
    title_entry.pack()
    
    def search():
      title = title_entry.get()
        
      if not title:
        messagebox.showerror("Error", "Please enter a book title.")
        return
        
      valid = self.app.library.search_book(title, self.db)
        
      if not valid['success']:
        messagebox.showerror("Error", valid['message'])
        return
        
      self.gui.display_books(valid['message'])
      
      window.destroy()
      
    Button(window, text="Search", command=search).pack()
      
  def update_book(self):
    window = Toplevel(self.root)
    window.title("Update Book")
    
    Label(window, text="Book ID").pack()
    enter_id_entry = Entry(window)
    enter_id_entry.pack()
    
    Label(window, text="Field").pack()
    field_combobox = ttk.Combobox(
      window,
      values=[
        "TITLE",
        "AUTHOR",
        "YEAR_PUBLISHED",
        "STOCK"
        ]
      )
    field_combobox.pack()
    
    Label(window, text="New value").pack()
    value_entry = Entry(window)
    value_entry.pack()
    
    def save():
      book_id = enter_id_entry.get()
      
      if not book_id:
        messagebox.showerror("Error", "Please enter a book ID to update.")
        return
      
      field = field_combobox.get()
      
      if field in ("TITLE", "AUTHOR"):
        value = value_entry.get()
        
        if not value:
          messagebox.showerror("Error", "Please enter a value.")
          return
          
      elif field in ("YEAR_PUBLISHED", "STOCK"):
        try:
          value = int(value_entry.get())
        except ValueError:
          messagebox.showerror("Error", "Please enter only a number.")
          return
        
      else:
        messagebox.showerror("Error", "Please select a field.")
        return
      
      if not value:
        messagebox.showerror("Error", "Please enter a valid info to update.")
        return
    
      valid = self.app.library.edit_book(book_id, field, value, self.db)
        
      if not valid['success']:
        logger.warning(f"UPDATE_BOOK_FAILED | REASON={valid['log_message']}")
        messagebox.showerror("Error", valid['message'])
        return
          
      logger.info("UPDATE_BOOK_SUCCESS")
      messagebox.showinfo("Success", valid['message'])
        
      self.db.commit()
        
      window.destroy()
        
    Button(window, text="Save", command=save).pack()
    
  def borrowed_books(self):
    valid = self.app.borrowed.show_students_borrowed(self.db)
      
    if not valid['success']:
      self.gui.status_label.config(text=valid['message'])
      return
      
    self.gui.display_students(valid['message'])
      
  def borrowed_history(self):
    logs = self.db.get_borrow_logs()
      
    if not logs:
      self.gui.status_label.config(text="No borrowed history yet.")
      
    self.gui.display_logs(logs)
      
  def returned_history(self):
    logs = self.db.get_return_logs()
      
    if not logs:
      self.gui.status_label.config(text="No returned history yet.")
    
    self.gui.display_logs(logs)
      
  def view_history(self):
    data = self.db.get_all_log()
    
    self.gui.display_logs(data)
  
  def stored_books(self):
    books = self.db.get_all_books()
    
    valid = self.app.library.show_available_books(books)
      
    if not valid['success']:
      self.gui.status_label.config(text=valid['message'])
      
    self.gui.display_books(valid['message'])
    
class LibraryFrame:
  def __init__(self, gui):
    self.gui = gui
    
    self.library_btn_frame = ttk.Frame(self.gui.library_tab)
    self.library_btn_frame.columnconfigure((0, 1, 2), weight=1)
    self.library_btn_frame.pack()
    
    self.book_tree_frame = ttk.Frame(self.gui.library_tab)
    self.book_tree_frame.pack(fill="both", expand=True)
      
    columns = (
      "book_id",
      "title",
      "author",
      "year_published",
      "stock"
    )
      
    headings = {
      "book_id": "ID",
      "title": "Title",
      "author": "Author",
      "year_published": "Year",
      "stock": "Stock"
    }
    
    widths = {
      "book_id": 80,
      "title": 200,
      "author": 200,
      "year_published": 100,
      "stock": 100
    }
      
    self.books_tree = create_tree(
      self.book_tree_frame,
      columns,
      headings,
      widths
      )
    
    scrollbar = ttk.Scrollbar(
      self.book_tree_frame,
      orient="vertical",
      command=self.books_tree.yview
      )
    
    self.books_tree.configure(yscrollcommand=scrollbar.set)
    
    self.books_tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    Button(self.library_btn_frame, text="Add", command=self.gui.controller.add_book).grid(row=0, column=0, sticky="ew")
    
    Button(self.library_btn_frame, text="Remove", command=self.gui.controller.remove_book).grid(row=0, column=1, sticky="ew")
    
    Button(self.library_btn_frame, text="Search", command=self.gui.controller.search_book).grid(row=0, column=2, sticky="ew")
    
    Button(self.library_btn_frame, text="Update", command=self.gui.controller.update_book).grid(row=1, column=0, sticky="ew")
    
    Button(self.library_btn_frame, text="View", command=self.gui.controller.stored_books).grid(row=1, column=1, sticky="ew")
    
class StudentFrame:
  def __init__(self, gui):
    self.gui = gui
    
    self.student_btn_frame = ttk.Frame(self.gui.students_tab)
    self.student_btn_frame.columnconfigure((0, 1, 2), weight=1)
    self.student_btn_frame.pack()
    
    self.student_tree_frame = ttk.Frame(self.gui.students_tab)
    self.student_tree_frame.pack(fill="both", expand=True)
      
    columns = (
      "name",
      "title",
      "book_id",
      "quantity"
    )
    
    headings = {
      "name": "Name",
      "title": "Title",
      "book_id": "ID",
      "quantity": "Quantity"
    }
    
    widths = {
      "name": 150,
      "title": 150,
      "book_id": 50,
      "quantity": 80
    }
      
    self.student_tree = create_tree(
      self.student_tree_frame,
      columns,
      headings,
      widths
      )
    
    Button(self.student_btn_frame, text="Borrow", command=self.gui.controller.borrow_book).grid(row=0, column=0, sticky="ew")
    
    Button(self.student_btn_frame, text="Return", command=self.gui.controller.return_book).grid(row=0, column=1, sticky="ew")
    
    Button(self.student_btn_frame, text="Search", command=self.gui.controller.search_student).grid(row=1, column=0, sticky="ew")
    
    Button(self.student_btn_frame, text="Borrowed", command=self.gui.controller.borrowed_books).grid(row=1, column=1, sticky="ew")
    
    scrollbar = ttk.Scrollbar(
      self.student_tree_frame,
      orient="vertical",
      command=self.student_tree.yview
      )
      
    self.student_tree.configure(yscrollcommand=scrollbar.set)
      
    scrollbar.pack(side="right", fill="y")
    self.student_tree.pack(fill="both", expand=True)
    
class LogFrame:
  def __init__(self, gui):
    self.gui = gui
    
    self.logs_btn_frame = ttk.Frame(self.gui.logs_tab)
    self.logs_btn_frame.columnconfigure((0, 1, 2), weight=1)
    self.logs_btn_frame.pack()
    
    self.logs_tree_frame = ttk.Frame(self.gui.logs_tab)
    self.logs_tree_frame.pack(fill="both", expand=True)
      
    columns = (
      "action",
      "student",
      "book_id",
      "quantity",
      "timestamp"
    )
    
    headings = {
      "action": "Action",
      "student": "Student",
      "book_id": "ID",
      "quantity": "Qty",
      "timestamp": "Timestamp"
    }
    
    widths = {
      "action": 140,
      "student": 150,
      "book_id": 80,
      "quantity": 80,
      "timestamp": 200
    }
      
    self.logs_tree = create_tree(
      self.logs_tree_frame,
      columns,
      headings,
      widths
      )
    
    Button(self.logs_btn_frame, text="Search", command=self.gui.controller.search_log_student).grid(row=0, column=0, sticky="ew")
    
    Button(self.logs_btn_frame, text="Borrowed", command=self.gui.controller.borrowed_history).grid(row=0, column=1, sticky="ew")
    
    Button(self.logs_btn_frame, text="Returned", command=self.gui.controller.returned_history).grid(row=1, column=0, sticky="ew")
    
    Button(self.logs_btn_frame, text="View", command=self.gui.controller.view_history).grid(row=1, column=1, sticky="ew")
    
    scrollbar = ttk.Scrollbar(
      self.logs_tree_frame,
      orient="vertical",
      command=self.logs_tree.yview
      )
      
    self.logs_tree.configure(yscrollcommand=scrollbar.set)
    
    scrollbar.pack(side="right", fill="y")
    self.logs_tree.pack(fill="both", expand=True)

if __name__ == "__main__":
  db = Database()
  
  root = Tk()
  library_gui = LibraryGUI(root, app, db)
  root.mainloop()