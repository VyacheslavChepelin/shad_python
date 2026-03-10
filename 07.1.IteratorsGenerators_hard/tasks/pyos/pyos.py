from queue import Queue
from abc import ABC, abstractmethod
from typing import Generator, Any


class SystemCall(ABC):
    """SystemCall yielded by Task to handle with Scheduler"""

    @abstractmethod
    def handle(self, scheduler: 'Scheduler', task: 'Task') -> bool:
        """
        :param scheduler: link to scheduler to manipulate with active tasks
        :param task: task which requested the system call
        :return: an indication that the task must be scheduled again
        """


Coroutine = Generator[SystemCall | None, Any, None]


class Task:
    def __init__(self, task_id: int, target: Coroutine) -> None:
        """
        :param task_id: id of the task
        :param target: coroutine to run. Coroutine can produce system calls.
        System calls are being executed by scheduler and the result sends back to coroutine.
        """
        self.id = task_id
        self.target = target
        self.result = None
        self.is_finished = False
        # todo: возможно надо is_stopped

    def set_syscall_result(self, result: Any) -> None:
        """
        Saves result of the last system call
        """
        self.result = result

    def step(self) -> SystemCall | None:
        """
        Performs one step of coroutine, i.e. sends result of last system call
        to coroutine (generator), gets yielded value and returns it.
        """
        if self.is_finished:
            return None
        try:
            return self.target.send(self.result)
        except StopIteration:
            self.is_finished = True
            return None


class Scheduler:
    """Scheduler to manipulate with tasks"""

    def __init__(self) -> None:
        self.task_id = 0
        self.task_queue: Queue[Task] = Queue()
        self.task_map: dict[int, Task] = {}  # task_id -> task
        self.wait_map: dict[int, list[Task]] = {}  # task_id -> list of waiting tasks #todo: почему листы

    def _schedule_task(self, task: Task) -> None:
        """
        Add task into task queue
        :param task: task to schedule for execution
        """
        self.task_queue.put(task)

    def new(self, target: Coroutine) -> int:
        """
        Create and schedule new task
        :param target: coroutine to wrap in task
        :return: id of newly created task
        """
        self.task_id += 1
        cur_task = Task(self.task_id, target)
        self.task_map[self.task_id] = cur_task
        self._schedule_task(cur_task)
        return self.task_id

    def exit_task(self, task_id: int) -> bool:
        """
        PRIVATE API: can be used only from scheduler itself or system calls
        Hint: do not forget to reschedule waiting tasks
        :param task_id: task to remove from scheduler
        :return: true if task id is valid
        """
        if task_id not in self.task_map:
            return False

        if task_id in self.wait_map:
            for task in self.wait_map[task_id]:
                self._schedule_task(task)
            del self.wait_map[task_id]
        del self.task_map[task_id]
        return True

    def wait_task(self, task_id: int, wait_id: int) -> bool:
        """
        PRIVATE API: can be used only from scheduler itself or system calls
        :param task_id: task to hold on until another task is finished
        :param wait_id: id of the other task to wait for
        :return: true if task and wait ids are valid task ids
        """
        if task_id not in self.task_map:
            return False
        if wait_id not in self.task_map:
            return False
        if wait_id not in self.wait_map:
            self.wait_map[wait_id] = []
        self.wait_map[wait_id].append(self.task_map[task_id])
        return True


    def run(self, ticks: int | None = None) -> None:
        """
        Executes tasks consequently, gets yielded system calls,
        handles them and reschedules task if needed
        :param ticks: number of iterations (task steps), infinite if not passed
        """
        cur_ticks = ticks
        while (cur_ticks is None or cur_ticks > 0) and not self.empty() and not self.task_queue.empty():
            task = self.task_queue.get()

            if task not in self.task_map.values():
                task.target.close()
                continue
            result = task.step()
            if task.is_finished:
                self.exit_task(task.id)
                continue
            else:
                if isinstance(result, SystemCall):
                    temp = result.handle(self, task)
                    if temp:
                        self._schedule_task(task)
                else:
                    task.set_syscall_result(result)
                    self._schedule_task(task)
            if cur_ticks is not None:
                cur_ticks -= 1

    def empty(self) -> bool:
        """Checks if there are some scheduled tasks"""
        return not bool(self.task_map)


class GetTid(SystemCall):
    """System call to get current task id"""

    def handle(self, scheduler: Scheduler, task: Task) -> bool:
        task.set_syscall_result(task.id)
        return True


class NewTask(SystemCall):
    """System call to create new task from target coroutine"""

    def __init__(self, target: Coroutine) -> None:
        self.target = target

    def handle(self, scheduler: Scheduler, task: Task) -> bool:
        new_id = scheduler.new(self.target)
        task.set_syscall_result(new_id)
        return True



class KillTask(SystemCall):
    """System call to kill task with particular task id"""

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id

    def handle(self, scheduler: Scheduler, task: Task) -> bool:
        task.set_syscall_result(scheduler.exit_task(self.task_id))
        return not task.id == self.task_id


class WaitTask(SystemCall):
    """System call to wait task with particular task id"""

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id

    def handle(self, scheduler: Scheduler, task: Task) -> bool:
        # Note: One shouldn't reschedule task which is waiting for another one.
        # But one must reschedule task if task id to wait for is invalid.
        task.set_syscall_result(scheduler.wait_task(task.id, self.task_id))
        return not task.result

