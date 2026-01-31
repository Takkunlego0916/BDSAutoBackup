# BDSAutoBackup.py（復元機能追加版）
import os, shutil, zipfile, threading, time, json, sys
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

CONFIG_FILE = "backup_config.json"

# ----------------- 設定読み込み -----------------
def load_config():
    if Path(CONFIG_FILE).exists():
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return json.load(f)
    else:
        default = {
            "server_executable":"bedrock_server.exe",
            "working_dir":".",
            "backup_interval":3600,
            "max_backups":24,
            "backup_targets":["worlds","resource_packs","behavior_packs"],
            "extra_files":[],
            "log_file":"bds_backup.log"
        }
        with open(CONFIG_FILE,"w",encoding="utf-8") as f:
            json.dump(default,f,indent=2)
        return default

config = load_config()

# ----------------- ログ -----------------
def log(msg):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{t}] {msg}"
    print(line)
    log_text.configure(state="normal")
    log_text.insert("end", line+"\n")
    log_text.see("end")
    log_text.configure(state="disabled")
    with open(config.get("log_file","bds_backup.log"),"a",encoding="utf-8") as f:
        f.write(line+"\n")

# ----------------- バックアップ -----------------
def create_zip(src_dir: Path, dest_zip: Path):
    tmp_zip = str(dest_zip)+".tmp"
    with zipfile.ZipFile(tmp_zip,'w',zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(src_dir):
            for f in files:
                full = Path(root)/f
                arcname = full.relative_to(src_dir.parent)
                zf.write(full, arcname)
    os.replace(tmp_zip,dest_zip)

def send_command(proc, cmd):
    try:
        if proc.poll() is None:
            proc.stdin.write(cmd+"\n")
            proc.stdin.flush()
            log(f"Sent command: {cmd}")
    except Exception as e:
        log(f"Failed send_command: {e}")

def prune_backups():
    backups = sorted(Path("backups").glob("bds_backup_*.zip"))
    if len(backups) > config.get("max_backups",24):
        for old in backups[:len(backups)-config.get("max_backups",24)]:
            try: old.unlink(); log(f"Deleted old backup {old}")
            except: pass

backup_history = []

def update_history(zip_path=None):
    if zip_path is not None:
        backup_history.insert(0, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -> {zip_path.name}")
        if len(backup_history) > 50: backup_history.pop()

    history_list.delete(0,tk.END)
    for h in backup_history: history_list.insert(tk.END,h)

    restore_list.delete(0,tk.END)
    backups_folder = Path("backups")
    for z in sorted(backups_folder.glob("bds_backup_*.zip"),reverse=True):
        restore_list.insert(tk.END,z.name)


def do_backup(proc=None):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = Path("backups"); dest.mkdir(exist_ok=True)
    backup_zip = dest / f"bds_backup_{timestamp}.zip"
    try:
        if proc: send_command(proc,"save hold"); time.sleep(3)

        temp_dir = Path(".bds_backup_temp")
        if temp_dir.exists(): shutil.rmtree(temp_dir)
        temp_dir.mkdir()

        for item in config["backup_targets"]:
            src = Path(config["working_dir"])/item
            if src.exists():
                dst = temp_dir/item
                if src.is_dir(): shutil.copytree(src,dst)
                else: shutil.copy2(src,dst)
            else: log(f"Target not found: {src}")

        for item in config["extra_files"]:
            src = Path(config["working_dir"])/item
            if src.exists():
                dst = temp_dir/src.name
                if src.is_dir(): shutil.copytree(src,dst)
                else: shutil.copy2(src,dst)
            else: log(f"Extra file not found: {src}")

        create_zip(temp_dir, backup_zip)
        shutil.rmtree(temp_dir)
        log(f"Backup completed: {backup_zip}")
    except Exception as e:
        log(f"Backup failed: {e}")
    finally:
        if proc: send_command(proc,"save resume")
    prune_backups()
    update_history(backup_zip)

# ----------------- 復元 -----------------
def restore_backup(zip_name=None):
    try:
        if zip_name is None:
            zip_path = filedialog.askopenfilename(title="Select Backup Zip", filetypes=[("Zip Files","*.zip")])
            if not zip_path: return
            zip_path = Path(zip_path)
        else:
            zip_path = Path("backups")/zip_name
        if not zip_path.exists():
            messagebox.showerror("Error","Backup not found")
            return

        # 現在フォルダを一時保存
        temp_save = Path(".restore_backup")
        if temp_save.exists(): shutil.rmtree(temp_save)
        temp_save.mkdir()
        for item in config["backup_targets"]+config["extra_files"]:
            src = Path(config["working_dir"])/item
            if src.exists():
                dst = temp_save/src.name
                if src.is_dir(): shutil.copytree(src,dst)
                else: shutil.copy2(src,dst)

        # zip解凍
        with zipfile.ZipFile(zip_path,'r') as zf:
            zf.extractall(Path(config["working_dir"]))
        log(f"Backup restored: {zip_path.name}")
        messagebox.showinfo("Restored",f"Backup restored: {zip_path.name}")
    except Exception as e:
        log(f"Restore failed: {e}")
        messagebox.showerror("Error",f"Restore failed: {e}")

# ----------------- 自動バックアップ -----------------
def backup_loop(proc=None):
    while True:
        time.sleep(config.get("backup_interval",3600))
        threading.Thread(target=do_backup,daemon=True).start()

# ----------------- GUI -----------------
root = tk.Tk()
root.title("BDS Auto Backup")
root.geometry("650x550")

tab_control = ttk.Notebook(root)
tab_basic = ttk.Frame(tab_control)
tab_targets = ttk.Frame(tab_control)
tab_actions = ttk.Frame(tab_control)
tab_control.add(tab_basic,text="Basic Settings")
tab_control.add(tab_targets,text="Backup Targets")
tab_control.add(tab_actions,text="Actions")
tab_control.pack(expand=1,fill="both")

# --- Basic Settings タブ ---
ttk.Label(tab_basic,text="Server Executable:").grid(row=0,column=0,sticky="w",padx=5,pady=5)
server_path_var = tk.StringVar(value=config.get("server_executable"))
ttk.Entry(tab_basic,textvariable=server_path_var,width=40).grid(row=0,column=1,padx=5,pady=5)
ttk.Button(tab_basic,text="Browse",command=lambda:server_path_var.set(filedialog.askopenfilename(title="Select bedrock_server.exe"))).grid(row=0,column=2,padx=5,pady=5)

ttk.Label(tab_basic,text="Working Directory:").grid(row=1,column=0,sticky="w",padx=5,pady=5)
working_dir_var = tk.StringVar(value=config.get("working_dir"))
ttk.Entry(tab_basic,textvariable=working_dir_var,width=40).grid(row=1,column=1,padx=5,pady=5)
ttk.Button(tab_basic,text="Browse",command=lambda:working_dir_var.set(filedialog.askdirectory(title="Select Working Directory"))).grid(row=1,column=2,padx=5,pady=5)

ttk.Label(tab_basic,text="Backup Interval (sec):").grid(row=2,column=0,sticky="w",padx=5,pady=5)
interval_var = tk.IntVar(value=config.get("backup_interval"))
ttk.Entry(tab_basic,textvariable=interval_var,width=10).grid(row=2,column=1,padx=5,pady=5)

ttk.Label(tab_basic,text="Max Backups:").grid(row=3,column=0,sticky="w",padx=5,pady=5)
max_var = tk.IntVar(value=config.get("max_backups"))
ttk.Entry(tab_basic,textvariable=max_var,width=10).grid(row=3,column=1,padx=5,pady=5)

# --- Backup Targets タブ ---
targets_frame = ttk.LabelFrame(tab_targets,text="Folders")
targets_frame.pack(fill="x",padx=5,pady=5)
vars_targets = {}
for t in ["worlds","resource_packs","behavior_packs"]:
    var = tk.BooleanVar(value=(t in config["backup_targets"]))
    vars_targets[t]=var
    ttk.Checkbutton(targets_frame,text=t,variable=var).pack(anchor="w")

extras_frame = ttk.LabelFrame(tab_targets,text="Extra Files")
extras_frame.pack(fill="x",padx=5,pady=5)
vars_extra = {}
for t in ["server.properties","allowlist.json","config"]:
    var = tk.BooleanVar(value=(t in config["extra_files"]))
    vars_extra[t]=var
    ttk.Checkbutton(extras_frame,text=t,variable=var).pack(anchor="w")

ttk.Button(tab_targets,text="Save Config",command=lambda:save_config()).pack(pady=5)
def save_config():
    config["server_executable"]=server_path_var.get()
    config["working_dir"]=working_dir_var.get()
    config["backup_interval"]=interval_var.get()
    config["max_backups"]=max_var.get()
    config["backup_targets"]=[k for k,v in vars_targets.items() if v.get()]
    config["extra_files"]=[k for k,v in vars_extra.items() if v.get()]
    with open(CONFIG_FILE,"w",encoding="utf-8") as f: json.dump(config,f,indent=2)
    messagebox.showinfo("Saved","Config saved successfully")

# --- Actions タブ ---
actions_frame = ttk.Frame(tab_actions)
actions_frame.pack(fill="x",padx=5,pady=5)
ttk.Button(actions_frame,text="Manual Backup",command=lambda:threading.Thread(target=do_backup,daemon=True).start()).pack(pady=5)

ttk.Label(tab_actions,text="Backup History:").pack(anchor="w",padx=5)
history_list = tk.Listbox(tab_actions,height=6)
history_list.pack(fill="x",padx=5,pady=5)

ttk.Label(tab_actions,text="Restore Backup:").pack(anchor="w",padx=5)
restore_list = tk.Listbox(tab_actions,height=6)
restore_list.pack(fill="x",padx=5,pady=5)
ttk.Button(tab_actions,text="Restore Selected Backup",command=lambda:threading.Thread(target=lambda:restore_backup(restore_list.get(tk.ACTIVE) if restore_list.curselection() else None),daemon=True).start()).pack(pady=5)

ttk.Label(tab_actions,text="Log:").pack(anchor="w",padx=5)
log_text = tk.Text(tab_actions,height=10,state="disabled")
log_text.pack(fill="both",expand=True,padx=5,pady=5)

# 自動バックアップスレッド
threading.Thread(target=backup_loop,daemon=True).start()

# 履歴初期読み込み
update_history(None)

root.mainloop()
