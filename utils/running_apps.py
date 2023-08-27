import psutil

def get_running_processes(output_type=None):
    running_processes = {}

    for proc in psutil.process_iter(attrs=['pid', 'name', 'ppid']):
        try:
            process_info = proc.info
            pid = process_info['pid']
            name = process_info['name']
            ppid = process_info['ppid']

            if ppid in running_processes:
                parent_name = running_processes[ppid]
                if pid > parent_name[0]:
                    running_processes[ppid] = (pid, name)
            else:
                running_processes[ppid] = (pid, name)

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if output_type == "name":
        return list(set(info[1] for info in running_processes.values()))
    elif output_type == "pid":
        return list(pid for pid, _ in running_processes.values())
    else:
        for parent_pid, (max_pid, app_name) in running_processes.items():
            print(f"PID: {max_pid} - App Name: {app_name}")

def main():
    get_running_processes()
    name_test = get_running_processes("name")
    pid_test = get_running_processes("pid")
    print(name_test, pid_test)

if __name__ == "__main__":
    main()
