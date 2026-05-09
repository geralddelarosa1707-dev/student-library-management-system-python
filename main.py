from logger import logger
from datetime import datetime
import json
import os

print("Welcome to Student Library Management System!")

menu = {
  "ADD": "Add new book",
  "REMOVE": "Remove book",
  "BORROW": "Borrowed book",
  "RETURN": "Returned book",
  "SEARCH-S": "Search student",
  "SEARCH-LS": "Search log by student",
  "SEARCH-B": "Search book",
  "UPDATE-B": "Update book info",
  "VIEW": "View borrowed books per students",
  "VIEW-BH": "View borrowed history",
  "VIEW-RH": "View returned history",
  "VIEW-H": "View history",
  "CHECK": "Check available books"
}

def show_menu(menu):
  print("\n--------------MENU--------------")
  for option, detail in menu.items():
    print(f"{option}: {detail}")
  print("--------------------------------")

class Book:
  def __init__(self, title, author, year_published, stock):
    self.title = title
    self.author = author
    self.year_published = year_published
    self.stock = stock
    
  def to_dict(self):
    return {
      "title": self.title,
      "author": self.author,
      "year_published": self.year_published,
      "stock": self.stock
    }
    
class StudentsBorrowed:
  def __init__(self):
    self.students_borrowed = {}
    
  def show_students_borrowed(self, app):
    books = app.library.books
    
    output = []
    
    if not self.students_borrowed:
      return False, "There are no students who have borrowed books yet."
    
    for student, book_borrowed in self.students_borrowed.items():
      
      if not book_borrowed:
        output.append(f"{student}: Didn't borrow")
        continue
      
      output.append(f"{student}:")
      
      for book_id, quantity in book_borrowed.items():
        book = books.get(book_id)
        
        if book is None:
          output.append(f" - Unknown book ({book_id})")
        else:
          output.append(f" - {book.title} ({book_id}) x{quantity}")
  
    return True, "\n".join(output)
    
  def search_student(self, name, app):
    books = app.library.books
    
    output = []
      
    if name not in self.students_borrowed:
      return False, "\nStudent not found."
        
    book_borrowed = self.students_borrowed[name]
        
    if not book_borrowed:
      return False, f"\n{name}: Didn't borrow"
      
    for book_id, quantity in book_borrowed.items():
      info = books.get(book_id)
      
      if info is None:
        output.append(f" - Unknown book ({book_id})")
      else:
        output.append(f" - {info.title} ({book_id}) x{quantity}")
        
    return True, f"{name}:\n" + "\n".join(output)
    
  def borrow_book(self, name, enter_book_id, info, num_books_borrowed):
    info.stock -= num_books_borrowed
      
    borrowed = self.students_borrowed
      
    borrowed.setdefault(name, {})
        
    borrowed[name][enter_book_id] = borrowed[name].get(enter_book_id, 0) + num_books_borrowed
  
class BookManager:
  def __init__(self):
    self.books = {}
    
  def show_available_books(self):
    output = []
    
    if not self.books:
      return False, "There are no books available yet."
  
    for book_id, info in self.books.items():
      output.append(f"{book_id}: '{info.title}' {info.author} - {info.year_published} : x{info.stock}")
  
    return True, "\n".join(output)
    
  def can_add_book(self, enter_id):
    if not enter_id:
      return False, "\nPlease enter a book ID.", "BOOK_ID_NOT_PROVIDED"
      
    if enter_id in self.books:
      return False, "\nID already exist", "ID ALREADY EXIST."
    
    return True, "\nAdded successfully!", None
  
  def can_remove_book(self, remove_book, info, app):
    borrowed_books = app.borrowed.students_borrowed
    
    output = []
    
    if not remove_book:
      return False, "Please enter a book ID.", "BOOK_ID_NOT_PROVIDED"
    
    if remove_book not in self.books:
      return False, f"{remove_book} Book ID not found.", "BOOK_ID_NOT_FOUND"
      
    for books in borrowed_books.values():
      if remove_book in books:
        output.append("Cannot remove. Some student still borrowed this book.")
        return False, "\n".join(output), "CANNOT_REMOVE,BOOK_STILL_BORROWED"
      
    return True, f"\n'{info.title}' removed successfully!", None
  
  def can_borrow(self, enter_book_id):
    if not enter_book_id:
      return False, "\nPlease enter a book ID.", "BOOK_ID_NOT_PROVIDED"
      
    if enter_book_id not in self.books:
      return False, "\nBook not found in the system.", "BOOK_NOT_FOUND"
    
    return True, "\nBorrowed successfully!", None
  
  def can_return(self, enter_book_id, check_book):
    if not enter_book_id:
      return False, "\nPlease enter a book ID.", "BOOK_ID_NOT_PROVIDED"
        
    if enter_book_id not in check_book:
      return False, "\nThe student didn't borrow the book.", "STUDENT_DIDN'T_BORROW_BOOK"
  
    return True, "\nReturned successfully!", None
    
  def return_book(self, name, enter_book_id, borrowed, quantity_borrowed, num_books_returned):
    info = self.books[enter_book_id]
      
    info.stock += num_books_returned
      
    remaining = quantity_borrowed - num_books_returned
      
    if remaining > 0:
      borrowed[name][enter_book_id] = remaining
    else:
      borrowed[name].pop(enter_book_id)
        
      if not borrowed[name]:
        borrowed.pop(name)
    
  def search_book(self, title):
    found = False
    
    output = []
      
    for book_id, info in self.books.items():
      if title.lower() in info.title.lower():
        output.append(f"{book_id}: '{info.title}' - {info.author} {info.year_published}: x{info.stock}")
        found = True
      
    if not found:
      return False, "\nBook not found."
      
    return True, "\n".join(output)
    
  def update_book(self, book_id, field, value):
    books = self.books
    
    if book_id not in books:
      return False, f"\n({book_id}) book ID not found.", f"({book_id})_BOOK_ID_NOT_FOUND"
      
    info = books[book_id]
        
    if field == "TITLE":
      info.title = value
          
    elif field == "AUTHOR":
      info.author = value
          
    elif field == "YEAR_PUBLISHED":
      if value < 1000 or value > 9999:
        return False, "\nPlease enter a valid year.", "NOT_VALID_YEAR"
      info.year_published = value
          
    elif field == "STOCK":
      if value < 0:
        return False, "\nStock cannot be negative.", "NOT_VALID_STOCK"
      info.stock = value
      
    return True, "\nUpdated successfully!", None
    
class App:
  def __init__(self):
    self.borrowed = StudentsBorrowed()
    self.library = BookManager()
    
app = App()
  
def load_data(app):
  try:
    with open("library_data.json", "r") as file:
      data = json.load(file)
      
      if not isinstance(data, dict):
        print("\nInvalid file format.")
        return
        
      app.library.books = {}
      
      books = data.get("books", {})
      
      if not isinstance(books, dict):
        books = {}
      
      for book_id, info in books.items():
        if not isinstance(book_id, str):
          continue
        
        try:
          book = Book(
            info["title"],
            info["author"],
            info["year_published"],
            info["stock"]
            )
          app.library.books[book_id] = book
        except (KeyError, TypeError):
          continue
        
      students = data.get("students_borrowed", {})
      
      if not isinstance(students, dict):
        students = {}
      else:
        cleaned = {}
        
        for name, books in students.items():
          if not isinstance(name, str):
            continue
          
          if not isinstance(books, dict):
            continue
          
          valid_books = {}
          
          for book_id, qty in books.items():
            if isinstance(book_id, str) and isinstance(qty, int) and qty > 0:
              valid_books[book_id] = qty
          
          if valid_books:
            cleaned[name] = valid_books
            
        students = cleaned
        
      app.borrowed.students_borrowed = students
      
  except FileNotFoundError:
    pass
    
  except json.JSONDecodeError:
    logger.error("DATA_FILE_CORRUPTED | REASON=JSONDecodeError")
    print("\nWarning: Data file is corrupted. Starting fresh.")
    
def save_data(app):
  temp_file = "library_data.json.tmp"
  main_file = "library_data.json"
  
  try:
    books = {
      book_id: info.to_dict() for book_id, info in app.library.books.items()
    }
  
    data = {
      "books": books,
      "students_borrowed": app.borrowed.students_borrowed
    }
      
    with open(temp_file, "w") as file:
      json.dump(data, file, indent=4)
      
      file.flush()
      os.fsync(file.fileno())
      
    os.replace(temp_file, main_file)
  except Exception as e:
    logger.error(f"ERROR_SAVING_DATA | REASON={e}")
    print("\nError saving data:", e)
    
def read_log():
  logs = []
  
  try:
    with open("audit_log.jsonl", "r") as file:
      for line in file:
        logs.append(json.loads(line))
  
  except FileNotFoundError:
    return []
    
  except json.JSONDecodeError:
    logger.error("LOG_FILE_CORRUPTED | REASON=JSONDecodeError")
    print("Log file corrupted.")
    return []
      
  return logs
  
def get_log_by_borrow():
  return [log for log in read_log() if (log.get("action") or "") == "BORROW"]
  
def get_log_by_return():
  return [log for log in read_log() if (log.get("action") or "") == "RETURN"]
  
def get_log_by_student(name):
  return [log for log in read_log() if (log.get("student") or "") == name]
    
def log_action(action, student, book_id, quantity):
  log_file = "audit_log.jsonl"
  
  new_entry = {
    "action": action.upper(),
    "student": student.upper(),
    "book_id": book_id,
    "quantity": quantity,
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  }
      
  try:
    with open(log_file, "a") as file:
      file.write(json.dumps(new_entry) + "\n")
      
  except Exception as e:
    logger.error(f"LOGGING_ERROR | REASON={e}")
    print("\nLogging error:", e)

def run_program(app):
  while True:
    show_menu(menu)
  
    ask_choice = input("\nWhat would you like to do: ").strip().upper()
  
    if ask_choice == "ADD":
      enter_id = input("\nEnter book ID (exa.B001): ").strip().upper()
      
      success, message, reason = app.library.can_add_book(enter_id)
      
      if not success:
        logger.warning(f"ADD_BOOK_FAILED | REASON={reason}")
        print(message)
        continue
    
      title = input("\nEnter the Title: ")
      
      if not title:
        print("\nPlease enter a title.")
        continue
    
      author = input("\nEnter the Author: ")
      
      if not author:
        print("\nPlease enter an author.")
        continue
    
      try:
        year_published = int(input("\nEnter Year published: "))
      except ValueError:
        print("\nPlease enter only a number")
        continue
      
      try:
        stock = int(input("\nEnter the number of Stock: "))
      except ValueError:
        print("\nPlease enter only a number.")
        continue
      
      book = Book(title, author, year_published, stock)
    
      app.library.books[enter_id] = book
      
      logger.info("ADD_BOOK_SUCCESS")
      print(message)
      save_data(app)
    
      input("\nPress Enter to continue...")
      
    elif ask_choice == "REMOVE":
      remove_book = input("\nEnter book ID to remove: ").strip().upper()
      
      info = app.library.books.get(remove_book)
      
      success, message, reason = app.library.can_remove_book(remove_book, info, app)
      
      if not success:
        logger.warning(f"REMOVE_BOOK_FAILED | REASON={reason}")
        print(message)
        continue
        
      confirm = input(f"\nAre you sure you want to remove '{info.title}' (y/n): ").lower()
        
      if confirm != "y":
        print("\nRemoving cancelled!")
        continue
      
      book = app.library.books.pop(remove_book)
      
      if book is None:
        continue
      
      logger.info("REMOVE_BOOK_SUCCESS")
      print(message)
      save_data(app)
       
      input("\nPress Enter to continue...")
    
    elif ask_choice == "BORROW":
      name = input("\nEnter Name: ").strip().upper()
      
      if not name:
        print("\nPlease enter a name.")
        continue
    
      enter_book_id = input("\nEnter the book ID borrowed: ").strip().upper()
      
      success, message, reason = app.library.can_borrow(enter_book_id)
      
      if not success:
        logger.warning(f"BORROW_BOOK_FAILED | REASON={reason}")
        print(message)
        continue
      
      books = app.library.books
      
      info = books[enter_book_id]
      
      try:
        num_books_borrowed = int(input("\nEnter number of books borrowed: "))
      except ValueError:
        print("\nPlease enter only a number.")
        continue
      
      if num_books_borrowed <= 0:
        print("\nPlease enter a valid number.")
        continue
        
      if info.stock == 0:
        print("\nOut of stock.")
        continue
      
      if num_books_borrowed > info.stock:
        print(f"\nThere are only {info.stock} stock/s.")
        continue
      
      app.borrowed.borrow_book(name, enter_book_id, info, num_books_borrowed)
      
      logger.info("BORROW_BOOK_SUCCESS")
      print(message)
      save_data(app)
      
      log_action("BORROW", name, enter_book_id, num_books_borrowed)
      
      input("\nPress Enter to continue...")
        
    elif ask_choice == "RETURN":
      name = input("\nEnter Name: ").strip().upper()
      
      if not name:
        print("\nPlease enter a name.")
        continue
      
      borrowed = app.borrowed.students_borrowed
      
      if name not in borrowed:
        print("\nStudent not found.")
        continue
        
      check_book = borrowed[name]
      
      if not check_book:
        print("\nStudent didn't borrow any book.")
        continue
        
      enter_book_id = input("\nEnter the book ID returned: ").strip().upper()
        
      success, message, reason = app.library.can_return(enter_book_id, check_book)
        
      if not success:
        logger.warning(f"RETURN_BOOK_FAILED | REASON={reason}")
        print(message)
        continue
      
      try:
        num_books_returned = int(input("\nEnter number of books returned: "))
      except ValueError:
        print("\nPlease enter only a number.")
        continue
      
      if num_books_returned <= 0:
        print("\nPlease enter a valid number.")
        continue
      
      quantity_borrowed = borrowed[name][enter_book_id]
      
      if num_books_returned > quantity_borrowed:
        print(f"\nStudent only borrowed {quantity_borrowed} copy/copies.")
        continue
      
      app.library.return_book(name, enter_book_id, borrowed, quantity_borrowed, num_books_returned)
      
      logger.info("RETURN_BOOK_SUCCESS")
      print(message)
      save_data(app)
      
      log_action("RETURN", name, enter_book_id, num_books_returned)
        
      input("\nPress Enter to continue...")
      
    elif ask_choice == "SEARCH-S":
      name = input("\nEnter student name: ").strip().upper()
      
      if not name:
        print("\nPlease enter a name.")
        continue
      
      success, message = app.borrowed.search_student(name, app)
      
      if not success:
        print(message)
        continue
      
      print(message)
      input("\nPress Enter to continue...")
      
    elif ask_choice == "SEARCH-LS":
      name = input("Enter Name: ").strip().upper()
      
      if not name:
        print("Please enter a name")
        continue
      
      logs = get_log_by_student(name)
      
      if not logs:
        print(f"There are no history with {name}")
        continue
      
      print("\n------------------STUDENT----------------")
      
      for log in logs:
        print("-" * 20)
        for key, info in log.items():
          print(f"{key}: {info}")
          
      print("-----------------------------------------")
      input("\nPress Enter to continue...")
      
    elif ask_choice == "SEARCH-B":
      title = input("\nEnter the title of the book: ").strip()
      
      if not title:
        print("\nPlease enter a book title.")
        continue
      
      success, message = app.library.search_book(title)
      
      if not success:
        print(message)
        continue
      
      print(message)
      input("\nPress Enter to continue...")
      
    elif ask_choice == "UPDATE-B":
      book_id = input("\nEnter book ID: ").strip().upper()
      
      if not book_id:
        print("\nPlease enter a book ID to update.")
        continue
      
      print("\nUpdate Options: TITLE | AUTHOR | YEAR_PUBLISHED | STOCK")
      
      field = input("\nWhat would you like to update: ").strip().upper()
      
      value = None
      
      if field == "TITLE":
        value = input("\nEnter book title: ")
        if not value:
          print("\nPlease enter a book title.")
          continue
        
      elif field == "AUTHOR":
        value = input("\nEnter book author: ")
        if not value:
          print("\nPlease enter a book author.")
          continue
        
      elif field == "YEAR_PUBLISHED":
        try:
          value = int(input("\nEnter year published: "))
        except ValueError:
          print("\nPlease enter only a number.")
          continue
        
      elif field == "STOCK":
        try:
          value = int(input("\nEnter stock: "))
        except ValueError:
          print("\nPlease enter only a number.")
          continue
        
      else:
        print("\nPlease enter a valid info to update.")
        continue
      
      success, message, reason = app.library.update_book(book_id, field, value)
      
      if not success:
        logger.warning(f"UPDATE_BOOK_FAILED | REASON={reason}")
        print(message)
        continue
        
      logger.info("UPDATE_BOOK_SUCCESS")
      print(message)
      save_data(app)
        
      input("\nPress Enter to continue...")
    
    elif ask_choice == "VIEW":
      print("\n-------------STUDENTS BORROWED---------------")
      
      success, message = app.borrowed.show_students_borrowed(app)
      
      if not success:
        print(message)
        continue
      
      print(message)
      print("---------------------------------------------")
      input("\nPress Enter to continue...")
      
    elif ask_choice == "VIEW-BH":
      logs = get_log_by_borrow()
      
      if not logs:
        print("No borrowed history yet.")
        continue
      
      print("\n------------------BORROW-----------------")
      
      for log in logs:
        print("-" * 20)
        for key, info in log.items():
          print(f"{key}: {info}")
          
      print("-----------------------------------------")
      input("\nPress Enter to continue...")
      
    elif ask_choice == "VIEW-RH":
      logs = get_log_by_return()
      
      if not logs:
        print("No returned history yet.")
        continue
      
      print("\n------------------RETURN-----------------")
    
      for log in logs:
        print("-" * 20)
        for key, info in log.items():
          print(f"{key}: {info}")
          
      print("-----------------------------------------")
      input("\nPress Enter to continue...")
      
    elif ask_choice == "VIEW-H":
      logs = read_log()
      
      print("\n------------------HISTORY----------------")
      
      if not logs:
        print("No history yet.")
        continue
      
      for log in logs:
        print("-" * 20)
        for key, info in log.items():
          print(f"{key}: {info}")
          
      print("-----------------------------------------")
      input("\nPress Enter to continue...")
  
    elif ask_choice == "CHECK":
      print("\n------------------BOOKS------------------")
      
      success, message = app.library.show_available_books()
      
      if not success:
        print(message)
        continue
      
      print(message)
      print("-----------------------------------------")
      input("\nPress Enter to continue...")
    
    else:
      print("\nPlease enter a valid option.")

if __name__ == "__main__":
  load_data(app)
  run_program(app)
