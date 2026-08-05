import sqlite3

from datetime import datetime

class Database:
  def __init__(self):
    self.conn = sqlite3.connect('library.db')
    self.conn.row_factory = sqlite3.Row
    self.cursor = self.conn.cursor()
    self.create_book_table()
    self.create_student_table()
    self.create_audit_log_table()
    
  def commit(self):
    self.conn.commit()

  def create_book_table(self):
    self.cursor.execute("""
    CREATE TABLE IF NOT EXISTS Books(
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    year_published INTEGER,
    stock INTEGER NOT NULL
    );
    """)
    self.conn.commit()
    
  def create_student_table(self):
    self.cursor.execute("""
    CREATE TABLE IF NOT EXISTS Students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    book_id TEXT NOT NULL,
    qty_borrowed INTEGER NOT NULL
    );
    """)
    self.conn.commit()
    
  def create_audit_log_table(self):
    self.cursor.execute("""
    CREATE TABLE IF NOT EXISTS AuditLog(
    action TEXT NOT NULL,
    student TEXT NOT NULL,
    book_id TEXT NOT NULL,
    quantity INTEGER,
    timestamp TEXT NOT NULL
    );
    """)
    self.conn.commit()
    
  def add_student_borrow(self, name, book_id, num_books_borrowed):
    self.cursor.execute("""
    INSERT INTO Students(name, book_id, qty_borrowed)
    VALUES(?, ?, ?)
    """, (name, book_id, num_books_borrowed))
    
  def insert_book(self, b_id, title, author, year_published, stock):
    self.cursor.execute("""
    INSERT INTO Books(
    id, title, author, year_published, stock
    )
    VALUES(?, ?, ?, ?, ?);
    """, (b_id, title, author, year_published, stock)
    )
      
  def log_action(self, action, student, book_id, quantity):
    self.cursor.execute("""
    INSERT INTO AuditLog(
    action, student, book_id, quantity, timestamp
    )
    VALUES(?, ?, ?, ?, ?);
    """, (action.upper(), student, book_id, quantity, datetime.now().strftime("%B %d, %Y - %H:%M %p"))
    )
    
  def get_all_books(self):
    self.cursor.execute("""
    SELECT * FROM Books;
    """)
    
    return self.cursor.fetchall()
    
  def get_book(self, book_id):
    self.cursor.execute("""
    SELECT * FROM Books
    WHERE id = ?;
    """, (book_id,))
        
    return self.cursor.fetchone()
    
  def get_book_by_title(self, title):
    return self.cursor.execute("""
    SELECT * FROM Books
    WHERE title = ?;
    """, (title,)).fetchall()
    
  def get_book_by_id(self, book_id):
    return self.cursor.execute("""
    SELECT id FROM Books WHERE id = ?
    """, (book_id,)).fetchone()
    
  def get_qty_borrowed(self, name, book_id):
    self.cursor.execute("""
    SELECT qty_borrowed FROM Students
    WHERE name = ? AND book_id = ?;
    """, (name, book_id))
      
    return self.cursor.fetchone()
    
  def get_students_borrowed(self, name):
    self.cursor.execute("""
    SELECT Students.name, Books.title, Students.book_id, Students.qty_borrowed
    FROM Students
    JOIN Books
    ON Students.book_id = Books.id
    WHERE name = ?;
    """, (name,))
    
    return self.cursor.fetchall()
    
  def show_all_students_borrowed(self):
    return self.cursor.execute("""
    SELECT Students.name, Books.title, Students.book_id, Students.qty_borrowed
    FROM Students
    JOIN Books
    ON Students.book_id = Books.id;
    """).fetchall()
    
  def get_student_by_name(self, name):
    return self.cursor.execute("""
    SELECT * FROM Students
    WHERE name = ?;
    """, (name,)).fetchone()
    
  def get_student_by_id(self, book_id):
    return self.cursor.execute("""
    SELECT * FROM Students
    WHERE book_id = ?;
    """, (book_id,)).fetchone()
    
  def get_student_return(self, name):
    return self.cursor.execute("""
    SELECT *, Books.id 
    FROM Students
    JOIN Books
    ON Students.book_id = Books.id
    WHERE name = ?;
    """, (name,)).fetchone()
    
  def get_borrow_logs(self):
    self.cursor.execute("""
    SELECT * FROM AuditLog
    WHERE action = 'BORROW';
    """)
    
    return self.cursor.fetchall()
    
  def get_return_logs(self):
    self.cursor.execute("""
    SELECT * FROM AuditLog
    WHERE action = 'RETURN';
    """)
    
    return self.cursor.fetchall()
    
  def get_log_student(self, name):
    self.cursor.execute("""
    SELECT * FROM AuditLog
    WHERE student = ?;
    """, (name,))
    
    return self.cursor.fetchall()
    
  def get_all_log(self):
    self.cursor.execute("""
    SELECT * FROM AuditLog;
    """)
    
    return self.cursor.fetchall()
    
  def decrease_stock(self, num_books_borrowed, book_id):
    self.cursor.execute("""
    UPDATE Books SET stock = stock - ?
    WHERE id = ?;
    """, (num_books_borrowed, book_id))
    
  def increase_stock(self, num_books_returned, book_id):
    self.cursor.execute("""
    UPDATE Books SET stock = stock + ?
    WHERE id = ?;
    """, (num_books_returned, book_id))
    
  def update_field(self, column, value, book_id):
    self.cursor.execute(f"""
    UPDATE Books SET {column} = ?
    WHERE id = ?
    """, (value, book_id))
    
  def update_qty_borrowed(self, num_books_borrowed, name, book_id):
    self.cursor.execute("""
    UPDATE Students SET qty_borrowed = ?
    WHERE name = ? AND book_id = ?;
    """, (num_books_borrowed, name, book_id))
    
  def delete_book(self, book_id):
    self.cursor.execute("""
    DELETE FROM Books
    WHERE id = ?;
    """, (book_id,))
    
  def delete_student(self, name, book_id):
    self.cursor.execute("""
    DELETE FROM Students
    WHERE name = ? AND book_id = ?;
    """, (name, book_id))