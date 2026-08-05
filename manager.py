def object_return(success, message, log_message):
  return {
    "success": success,
    "message": message,
    "log_message": log_message
  }
  
def read_return(success, message):
  return {
    "success": success,
    "message": message
  }

class Book:
  def __init__(self, b_id, title, author, year_published, stock):
    self.b_id = b_id
    self.title = title
    self.author = author
    self.year_published = year_published
    self.stock = stock
    
class StudentsManager:
  def students_borrowed(self, name, db):
    output = []
    
    stu_borrowed = db.get_students_borrowed(name)
    
    if not stu_borrowed:
      return read_return(False, f"{name} did not borrow any book.")
    
    for row in stu_borrowed:
      output.append({
        "name": row['name'],
        "title": row['title'],
        "book_id": row['book_id'],
        "quantity": row['qty_borrowed']
      })
  
    return read_return(True, output)
    
  def show_students_borrowed(self, db):
    output = []
    
    stu_borrowed = db.show_all_students_borrowed()
    
    if not stu_borrowed:
      return read_return(False, "There are no students who have borrowed books yet.")
    
    for row in stu_borrowed:
      output.append({
        "name": row['name'],
        "title": row['title'],
        "book_id": row['book_id'],
        "quantity": row['qty_borrowed']
      })
  
    return read_return(True, output)
    
  def search_student_filter(self, name, db):
    output = []
    
    stu_borrowed = db.get_student_by_name(name)
    
    if stu_borrowed is None:
      return read_return(False, "\nStudent not found.")
    
    rows = db.get_students_borrowed(name)
    
    for row in rows:
      output.append({
        "name": row['name'],
        "title": row['title'],
        "book_id": row['book_id'],
        "quantity": row['qty_borrowed']
      })
        
    return read_return(True, output)
    
  def borrow_book(self, name, enter_book_id, num_books_borrowed, db):
    db.decrease_stock(num_books_borrowed, enter_book_id)
    
    record = db.get_qty_borrowed(name, enter_book_id)
    
    if record is None:
      db.add_student_borrow(name, enter_book_id, num_books_borrowed)
    else:
      db.update_qty_borrowed(num_books_borrowed, name, enter_book_id)
  
class BookManager:
  def show_available_books(self, books):
    output = []
    
    if books is None:
      return read_return(False, "There are no books available yet.")
  
    for row in books:
      output.append({
        "book_id": row['id'],
        "title": row['title'],
        "author": row['author'],
        "year_published": row['year_published'],
        "stock": row['stock']
      })
  
    return read_return(True, output)
    
  def can_add_book(self, enter_id, db):
    if not enter_id:
      return object_return(False, "\nPlease enter a book ID.", "BOOK_ID_NOT_PROVIDED")
    
    book = db.get_book_by_id(enter_id)
      
    if book:
      return object_return(False, "\nID already exist", "ID ALREADY EXIST.")
    
    return object_return(True, "\nAdded successfully!", None)
  
  def can_remove_book(self, remove_book, db):
    if not remove_book:
      return object_return(False, "Please enter a book ID.", "BOOK_ID_NOT_PROVIDED")
      
    books = db.get_book(remove_book)
    
    if books is None:
      return object_return(False, f"{remove_book} Book ID not found.", "BOOK_ID_NOT_FOUND")
    
    if books is None:
      return object_return(False, f"{remove_book} Book ID not found.", "BOOK_ID_NOT_FOUND")
    
    borrowed = db.get_student_by_id(remove_book)
      
    if borrowed:
      return object_return(False, "Cannot remove. Some student still borrowed this book.", "CANNOT_REMOVE,BOOK_STILL_BORROWED")
      
    return object_return(True, f"\n'{books['title']}' removed successfully!", None)
  
  def can_borrow(self, enter_book_id, num_books_borrowed, db):
    if not enter_book_id:
      return object_return(False, "\nPlease enter a book ID.", "BOOK_ID_NOT_PROVIDED")
      
    books = db.get_book(enter_book_id)
      
    if books is None:
      return object_return(False, "Book not found in the system.", "BOOK_NOT_FOUND")
      
    if books['stock'] == 0:
      return object_return(False, "Out of stock.", "OUT_OF_STOCK")
        
    if num_books_borrowed > books['stock']:
      return object_return(False, f"There are only {info['stock']} stock/s.", "NOT_ENOUGH_STOCK")
    
    return object_return(True, "\nBorrowed successfully!", None)
  
  def can_return(self, name, enter_book_id, num_books_returned, db):
    if not enter_book_id:
      return object_return(False, "\nPlease enter a book ID.", "BOOK_ID_NOT_PROVIDED")
    
    check_book = db.get_student_return(name)
        
    if check_book is None:
      return object_return(False, "The student didn't borrow the book.", "STUDENT_DIDN'T_BORROW_BOOK")
      
    quantity_borrowed = db.get_qty_borrowed(name, enter_book_id)
      
    quantity = quantity_borrowed['qty_borrowed']
        
    if num_books_returned > quantity:
      return object_return(False, f"Student only borrowed {quantity} copy/copies.", "EXCEED'S_STUDENT_BORROWED")
  
    return object_return(True, "\nReturned successfully!", None)
    
  def return_book(self, name, enter_book_id, num_books_returned, db):
    db.increase_stock(num_books_returned, enter_book_id)
    
    quantity = db.get_qty_borrowed(name, enter_book_id)
    
    qty = quantity['qty_borrowed']
      
    remaining = qty - num_books_returned
      
    if remaining > 0:
      db.update_qty_borrowed(remaining, name, enter_book_id)
    else:
      db.delete_student(name, enter_book_id)
    
  def search_book(self, title, db):
    output = []
    
    rows = db.get_book_by_title(title)
    
    for row in rows:
      output.append({
        "book_id": row['id'],
        "title": row['title'],
        "author": row['author'],
        "year_published": row['year_published'],
        "stock": row['stock']
      })
      
    if not output:
      return read_return(False, "\nBook not found.")
      
    return read_return(True, output)
    
  def edit_book(self, book_id, field, value, db):
    books = db.get_book(book_id)
    
    if books is None:
      return object_return(False, f"\n({book_id}) book ID not found.", f"({book_id})_BOOK_ID_NOT_FOUND")
          
    if field == "YEAR_PUBLISHED":
      if value < 1000 or value > 9999:
        return object_return(False, "\nPlease enter a valid year.", "NOT_VALID_YEAR")
          
    elif field == "STOCK":
      if value < 0:
        return object_return(False, "\nStock cannot be negative.", "NOT_VALID_STOCK")
      
    allowed_fields = {
      "TITLE": "title",
      "AUTHOR": "author",
      "YEAR_PUBLISHED": "year_published",
      "STOCK": "stock"
    }
    
    column = allowed_fields[field]
      
    db.update_field(column, value, book_id)
      
    return object_return(True, "\nUpdated successfully!", None)
    
class App:
  def __init__(self):
    self.borrowed = StudentsManager()
    self.library = BookManager()
    
app = App()