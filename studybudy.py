import socketio
from twitchio.ext import commands
import threading

sio = socketio.Client()
user_tasks = {}  # Tasks directory for users
active_users = set()

def Init():
    """Initialize bot and WebSocket connection."""
    global bot
    sio.connect('http://localhost:5000')  # Replace with your SocketIO server URL

    # Set up Twitch bot with Streamlabs-compatible settings
    bot = commands.Bot(
        token='your_oauth_token',
        prefix='!',
        initial_channels=['your_channel']
    )
    threading.Thread(target=bot.run).start()

def Execute(data):
    """Handles commands (!task, !done, !tasklist, !clear)."""
    command = data.GetParam(0).lower()
    username = data.User
    task = data.Message[len(command) + 1:].strip()

    if command == "!task":
        add_task(username, task)
    elif command == "!done":
        mark_task_done(username, task)
    elif command == "!tasklist":
        show_task_list(username)
    elif command == "!clear":
        clear_tasks(username)

def add_task(username, task):
    """Adds a task and updates overlay."""
    if username not in user_tasks:
        user_tasks[username] = []
    user_tasks[username].append({'task': task, 'done': False})
    sio.emit('update_tasks', {'username': username, 'tasks': user_tasks[username]})
    Parent.SendStreamMessage(f"{username}, that thing you need to do '{task}' has been added!")

def mark_task_done(username, task):
    """Marks a task as done for a user."""
    if username in user_tasks:
        for t in user_tasks[username]:
            if t['task'].lower() == task.lower() and not t['done']:
                t['done'] = True
                sio.emit('update_tasks', {'username': username, 'tasks': user_tasks[username]})
                Parent.SendStreamMessage(f"Hey {username}, you did the '{task}' thing. GG!")
                return
    Parent.SendStreamMessage(f"{username}, task '{task}' not found or already completed!")

def show_task_list(username):
    """Displays user's task list."""
    tasks = user_tasks.get(username, [])
    formatted = ', '.join([t['task'] if not t['done'] else f"~~{t['task']}~~" for t in tasks])
    Parent.SendStreamMessage(f"{username}, the stuff you gotta do today is: {formatted}")

def clear_tasks(username):
    """Clears all tasks for a user."""
    user_tasks[username] = []
    sio.emit('update_tasks', {'username': username, 'tasks': []})
    Parent.SendStreamMessage(f"{username}, all that stuff has been yeeeeeted off your list.")
