import argparse
import sys
import json
import os
from datetime import date,datetime

# נגדיר את שם הקובץ כקבוע בראש הקובץ
FILE_NAME = "expenses.json"

# --- פונקציות עזר לשמירה וקריאה ---

def load_expenses():
    """קוראת את הנתונים מהקובץ. מחזירה רשימה ריקה אם הקובץ לא קיים."""
    if not os.path.exists(FILE_NAME):
        return [] # ריצה ראשונה - הקובץ עדיין לא קיים
    
    with open(FILE_NAME, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return [] # הגנה למקרה שהקובץ קיים אך ריק או פגום

def save_expenses(expenses):
    """שומרת את רשימת ההוצאות לקובץ ה-JSON בפורמט קריא."""
    with open(FILE_NAME, "w", encoding="utf-8") as file:
        json.dump(expenses, file, indent=4)


# --- שילוב בפונקציית הוספת ההוצאה ---

def add_expense(args):
    if args.amount <= 0:
        print("Error: Amount must be a positive number.")
        return

    # 1. טעינת ההוצאות הקיימות מהקובץ
    expenses = load_expenses()

    # 2. חישוב המזהה (ID) החדש
    if len(expenses) > 0:
        # מוצא את ה-ID הגבוה ביותר ומוסיף לו 1
        new_id = max(expense["id"] for expense in expenses) + 1
    else:
        new_id = 1 # הוצאה ראשונה אי פעם

    # 3. יצירת אובייקט ההוצאה החדש (מילון)
    new_expense = {
        "id": new_id,
        "date": date.today().isoformat(), # יצירת תאריך בפורמט YYYY-MM-DD
        "description": args.description,
        "amount": args.amount
    }

    # 4. הוספה לרשימה ושמירה חזרה לקובץ
    expenses.append(new_expense)
    save_expenses(expenses)

    print(f"Expense added successfully (ID: {new_id})")

def list_expenses(args):
    # 1. טעינת הנתונים
    expenses = load_expenses()
    
    # בדיקה האם יש בכלל הוצאות
    if not expenses:
        print("No expenses found.")
        return

    # 2. הדפסת כותרות הטבלה בצורה מיושרת
    # הסבר: <4 אומר "יישר לשמאל ושריין 4 תווים", כדי ליצור רווחים אחידים
    print(f"{'ID':<4} {'Date':<12} {'Description':<20} {'Amount':<10}")
    
    # 3. מעבר על כל ההוצאות והדפסת השורות
    for exp in expenses:
        # עיצוב הסכום כך שיציג 2 ספרות עשרוניות (.2f)
        amount_formatted = f"${exp['amount']:.2f}"
        print(f"{exp['id']:<4} {exp['date']:<12} {exp['description']:<20} {amount_formatted:<10}")


def delete_expense(args):
    # 1. טעינת הנתונים
    expenses = load_expenses()
    target_id = args.id
    
    # שמירת האורך המקורי כדי לדעת אם באמת נמחקה שורה
    initial_length = len(expenses)
    
    # 2. סינון הרשימה: שומרים רק את ההוצאות שה-ID שלהן *לא* שווה ל-ID שהוזן
    expenses = [exp for exp in expenses if exp["id"] != target_id]
    
    # 3. בדיקה אם בוצעה מחיקה ושמירה חזרה לקובץ
    if len(expenses) < initial_length:
        save_expenses(expenses)
        print("Expense deleted successfully")
    else:
        print(f"Error: Expense with ID {target_id} not found.")


def summarize_expenses(args):
    # 1. טעינת הנתונים
    expenses = load_expenses()
    
    if not expenses:
        print("No expenses found.")
        return

    # 2. אם המשתמש הזין חודש ספציפי
    if args.month:
        # וידוא תקינות קלט (חודש חייב להיות בין 1 ל-12)
        if not (1 <= args.month <= 12):
            print("Error: Month must be between 1 and 12.")
            return
            
        total = 0
        current_year = datetime.now().year
        
        # מעבר על ההוצאות וסינון לפי חודש ושנה נוכחית
        for exp in expenses:
            # המרת מחרוזת התאריך חזרה לאובייקט תאריך
            exp_date = datetime.strptime(exp["date"], "%Y-%m-%d")
            
            if exp_date.month == args.month and exp_date.year == current_year:
                total += exp["amount"]
                
        # המרת מספר החודש לשם החודש באנגלית (למשל 8 הופך ל-August) לתצוגה יפה
        month_name = datetime(current_year, args.month, 1).strftime("%B")
        print(f"Total expenses for {month_name}: ${total:.2f}")
        
    # 3. אם לא הוזן חודש - סוכמים את הכל
    else:
        # שימוש בפונקציית sum מקוצרת כדי לחבר את כל הסכומים
        total = sum(exp["amount"] for exp in expenses)
        print(f"Total expenses: ${total:.2f}")

def main():
    # הגדרת הנתב הראשי
    parser = argparse.ArgumentParser(description="Expense Tracker CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # פקודת Add
    add_parser = subparsers.add_parser("add", help="Add a new expense")
    add_parser.add_argument("--description", required=True, type=str, help="Description of the expense")
    add_parser.add_argument("--amount", required=True, type=float, help="Amount of the expense")
    add_parser.set_defaults(func=add_expense)

    # פקודת List
    list_parser = subparsers.add_parser("list", help="List all expenses")
    list_parser.set_defaults(func=list_expenses)

    # פקודת Delete
    delete_parser = subparsers.add_parser("delete", help="Delete an expense by ID")
    delete_parser.add_argument("--id", required=True, type=int, help="ID of the expense to delete")
    delete_parser.set_defaults(func=delete_expense)

    # פקודת Summary
    summary_parser = subparsers.add_parser("summary", help="Show summary of all expenses")
    summary_parser.add_argument("--month", type=int, help="Optional: Month number (1-12)")
    summary_parser.set_defaults(func=summarize_expenses)

    # פענוח הקלט מהמשתמש
    args = parser.parse_args()

    # ניתוב לפונקציה המתאימה (לפי מה שהוגדר ב-set_defaults)
    if args.command:
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
