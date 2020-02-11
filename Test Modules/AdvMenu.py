import sys, os
import curses

def draw_menu(stdscr):
    
    stdscr.addstr(0, 0, "Facial Recognition System Menu")
    stdscr.addstr(1, 0, "STATUS")
    stdscr.addstr(2, 0, "Door: ")
    stdscr.addstr(3, 0, "Active Keys: ")
    stdscr.addstr(4, 0, "List of Active Key(s)")
    stdscr.addstr(5, 0, "No.\tKey\tCreation Date & Time\tExpiration Date & Time")
    stdscr.refresh()
    curses.napms(5000)
    
    curses.endwin()

def main():
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    main()
