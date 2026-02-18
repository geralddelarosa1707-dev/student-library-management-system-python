import json
import os

print("Welcome to Student Library Management System!")

books = {}

students_borrowed = {}

menu = {
  "ADD": "Add new book",
  "REMOVE": "Remove book",
  "BORROW": "Borrowed book",
  "RETURN": "Returned book",
  "SEARCH-S": "Search student",
  "SEARCH-B": "Search book",
  "UPDATE-B": "Update book info",
  "VIEW": "View borrowed books per students",
  "CHECK": "Check available books"
}

def show_menu(menu):
  print("\n--------------MENU--------------")
  for option, detail in menu.items():
    print(f"{option}: {detail}")
  print("--------------------------------")
  
def can_add_book(books, enter_id):
  if not enter_id:
    print("\nPlease enter a book ID.")
    return False
      
  if enter_id in books:
    print("\nID already exist.")
    return False
    
  return True
  
def can_remove_book(books, students_borrowed, remove_book):
  if not remove_book:
    print("\nPlease enter a book ID.")
    return False
    
  if remove_book not in books:
    print(f"\n{remove_book} Book ID not found.")
    return False
      
  for student in students_borrowed:
    if remove_book in students_borrowed[student]:
      print("\nCannot remove. Some student still borrowed this book.")
      return False
      
  return True
  
def can_borrow(books, enter_book_id):
  if not enter_book_id:
    print("\nPlease enter a book ID.")
    return False
      
  if enter_book_id not in books:
    print("\nBook not found in the system.")
    return False
    
  return True
  
def can_return(enter_book_id, check_book):
  if not enter_book_id:
    print("\nPlease enter a book ID.")
    return False
        
  if enter_book_id not in check_book:
    print("\nThe student didn't borrow the book.")
    return False
  
  return True
  
def show_students_borrowed(students_borrowed, books):
  if not students_borrowed:
    print("\nThere are no students who have borrowed books yet.")
    return False
    
  print("\n-------------STUDENTS BORROWED---------------")
  for student, book_borrowed in students_borrowed.items():
    if not book_borrowed:
      print(f"{student.title()}: Didn't borrow")
    else:
      print(f"{student.title()}:")
      
      for book_id, quantity in book_borrowed.items():
        if book_id in books:
          title, author, year_published, stock = books[book_id]
          
          print(f" - {title} ({book_id}) x{quantity}")
          
        else:
          print(f" - Unknown book ({book_id})")
        
  print("---------------------------------------------")
  
  return True
  
def show_available_books(books):
  if not books:
    print("\nThere are no books available yet.")
    return False
    
  print("\n------------------BOOKS------------------")
  for book_id, info in books.items():
    title, author, year_published, stock = info
    
    print(f"{book_id}: '{title.title()}' {author.title()} - {year_published} : x{stock}")
  print("-----------------------------------------")
  
  return True
  
def load_data():
  if os.path.exists("library_data.json"):
    try:
      with open("library_data.json", "r") as file:
        data = json.load(file)
        return data.get("books", {}), data.get("students_borrowed", {})
    except json.JSONDecodeError:
      print("\nWarning: Data file is corrupted. Starting fresh.")
      
  return {}, {}
    
def save_data(books, students_borrowed):
  data = {
    "books": books,
    "students_borrowed": students_borrowed
  }
  
  with open("library_data.json", "w") as file:
    json.dump(data, file, indent=4)

def run_program():
  while True:
    show_menu(menu)
  
    ask_choice = input("\nWhat would you like to do: ").strip().upper()
  
    if ask_choice == "ADD":
      enter_id = input("\nEnter book ID (exa.B001): ").strip().upper()
      
      get_id = can_add_book(books, enter_id)
      
      if not get_id:
        continue
    
      title = input("\nEnter the Title: ").title()
      
      if not title:
        print("\nPlease enter a title.")
        continue
    
      author = input("\nEnter the Author: ").title()
      
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
    
      books[enter_id] = (title, author, year_published, stock)
    
      print("\nAdded successfully!")
      
      save_data(books, students_borrowed)
    
      input("\nPress Enter to continue...")
      
    elif ask_choice == "REMOVE":
      remove_book = input("\nEnter book ID to remove: ").strip().upper()
      
      if not can_remove_book(books, students_borrowed, remove_book):
        continue
    
      title, author, year_published, stock = books[remove_book]
        
      confirm = input(f"\nAre you sure you want to remove '{title.title()}' (y/n): ").lower()
        
      if confirm != "y":
        print("\nRemoving cancelled!")
        continue
        
      del books[remove_book]
        
      print(f"\n'{title.title()}' removed successfully!")
        
      save_data(books, students_borrowed)
       
      input("\nPress Enter to continue...")
    
    elif ask_choice == "BORROW":
      key_name = input("\nEnter Name: ").strip().upper()
      
      if not key_name:
        print("\nPlease enter a name.")
        continue
    
      enter_book_id = input("\nEnter the book ID borrowed: ").strip().upper()
      
      get_borrowed_book = can_borrow(books, enter_book_id)
      
      if not get_borrowed_book:
        continue
      
      title, author, year_published, stock = books[enter_book_id]
      
      try:
        num_books_borrowed = int(input("\nEnter number of books borrowed: "))
      except ValueError:
        print("\nPlease enter only a number.")
        continue
        
      if stock == 0:
        print("\nOut of stock.")
        continue
      
      if num_books_borrowed > stock:
        print(f"\nThere are only {stock} stock/s.")
        continue
        
      books[enter_book_id] = (title, author, year_published, stock - num_books_borrowed)
      
      students_borrowed.setdefault(key_name, {})
        
      students_borrowed[key_name][enter_book_id] = students_borrowed[key_name].get(enter_book_id, 0) + num_books_borrowed
    
      print("\nBorrowed successfully!")
      
      save_data(books, students_borrowed)
      
      input("\nPress Enter to continue...")
        
    elif ask_choice == "RETURN":
      key_name = input("\nEnter Name: ").strip().upper()
      
      if not key_name:
        print("\nPlease enter a name.")
        continue
      
      if key_name not in students_borrowed:
        print("\nStudent not found.")
        continue
        
      check_book = students_borrowed[key_name]
      
      if not check_book:
        print("\nStudent didn't borrow any book.")
        continue
        
      enter_book_id = input("\nEnter the book ID returned: ").strip().upper()
        
      get_returned_book = can_return(enter_book_id, check_book)
        
      if not get_returned_book:
        continue
      
      try:
        num_books_returned = int(input("\nEnter number of books returned: "))
      except ValueError:
        print("\nPlease enter only a number.")
        continue
      
      if num_books_returned <= 0:
        print("\nPlease enter a valid number.")
        continue
      
      quantity_borrowed = students_borrowed[key_name][enter_book_id]
      
      if num_books_returned > quantity_borrowed:
        print(f"\nStudent only borrowed {quantity_borrowed} copy/copies.")
        continue
      
      title, author, year_published, stock = books[enter_book_id]
      
      books[enter_book_id] = (title, author, year_published, stock + num_books_returned)
      
      remaining = quantity_borrowed - num_books_returned
      
      if remaining > 0:
        students_borrowed[key_name][enter_book_id] = remaining
      else:
        del students_borrowed[key_name][enter_book_id]
        
        if not students_borrowed[key_name]:
          del students_borrowed[key_name]
        
      print("\nReturned successfully!")
      
      save_data(books, students_borrowed)
        
      input("\nPress Enter to continue...")
      
    elif ask_choice == "SEARCH-S":
      student_name = input("\nEnter student name: ").strip().upper()
      
      if not student_name:
        print("\nPlease enter a name.")
        continue
      
      if student_name not in students_borrowed:
        print("\nStudent not found.")
        continue
        
      book_borrowed = students_borrowed[student_name]
        
      if not book_borrowed:
        print(f"\n{student_name.title()}: Didn't borrow")
      else:
        print(f"\n{student_name.title()}:")
      
      for book_id, quantity in book_borrowed.items():
        if book_id in books:
          title, author, year_published, stock = books[book_id]
          
          print(f" - {title} ({book_id}) x{quantity}")
          
        else:
          print(f" - Unknown book ({book_id})")
        
      input("\nPress Enter to continue...")
      
    elif ask_choice == "SEARCH-B":
      book_title = input("\nEnter the title of the book: ").strip().title()
      
      if not book_title:
        print("\nPlease enter a book title.")
        continue
      
      found = False
      
      for book_id, info in books.items():
        title, author, year_published, stock = info
        
        if book_title.lower() in title.lower():
          print(f"\n{book_id}: '{title.title()}' {author.title()} {year_published}: x{stock}")
          found = True
      
      if not found:
        print("\nBook not found.")
        continue
        
      input("\nPress Enter to continue...")
      
    elif ask_choice == "UPDATE-B":
      book_id = input("\nEnter book ID: ").strip().upper()
      
      if not book_id:
        print("\nPlease enter a book ID to update.")
        continue
      
      if book_id in books:
        title, author, year_published, stock = books[book_id]
        
        print("\nUpdate Options: TITLE | AUTHOR | YEAR_PUBLISHED | STOCK")
        
        info_to_update = input("\nWhat would you like to update: ").strip().upper()
        
        if info_to_update == "TITLE":
          update_title = input("\nEnter book title: ").title()
          
          if not update_title:
            print("\nPlease enter a book title.")
            continue
          
          title = update_title
          
        elif info_to_update == "AUTHOR":
          update_author = input("\nEnter book author: ").title()
          
          if not update_author:
            print("\nPlease enter a book author.")
            continue
          
          author = update_author
          
        elif info_to_update == "YEAR_PUBLISHED":
          try:
            update_year_published = int(input("\nEnter year published: "))
          except ValueError:
            print("\nPlease enter only a number.")
            continue
          
          year_published = update_year_published
          
        elif info_to_update == "STOCK":
          try:
            update_stock = int(input("\nEnter stock: "))
          except ValueError:
            print("\nPlease enter only a number.")
            continue
          
          if update_stock < 0:
            print("\nStock cannot be negative.")
            continue
          
          stock = update_stock
          
        else:
          print("\nPlease enter a valid info to update.")
          continue
        
        books[book_id] = (title, author, year_published, stock)
        
        print("\nUpdated successfully!")
        
        save_data(books, students_borrowed)
        
      else:
        print(f"({book_id}) book ID not found.")
        
      input("\nPress Enter to continue...")
    
    elif ask_choice == "VIEW":
      s_borrowed = show_students_borrowed(students_borrowed, books)
      
      input("\nPress Enter to continue...")
  
    elif ask_choice == "CHECK":
      avail_books = show_available_books(books)
      
      if not avail_books:
        continue
      
      input("\nPress Enter to continue...")
    
    else:
      print("\nPlease enter a valid option.")

if __name__ == "__main__":
  books, students_borrowed = load_data()
  run_program()