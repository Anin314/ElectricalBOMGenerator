# main.py
from views.main_view import MainView
import tkinter as tk


def main():
    """主函数"""
    root = tk.Tk()
    app = MainView(root)
    root.mainloop()


if __name__ == "__main__":

    main()


