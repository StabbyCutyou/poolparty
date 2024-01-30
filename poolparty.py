from multiprocessing import Pool
import os

def handle_result(_):
    print(f"[{os.getpid()} - INFO]: Handling result! This means no error happened in the child process for this task")

def handle_error(exc):
    print(f"[{os.getpid()} -  ERR]: Handling error {exc}! This means an error was raised *and* captured between parent and child process for this task")
    # We could re-raise here, push to sentry, etc

def main():
    # Pool A - doesn't raise, errors lost entirely
    print(f"[{os.getpid()} - INFO]: ================== Pool A - Silent Failures ========================== ")
    print(f"[{os.getpid()} - INFO]: Let's try an apply_async with no error callback!")
    poolA = Pool(1)
    arA = poolA.apply_async(work_fail)
    print(f"[{os.getpid()} - INFO]: Closing Pool A!")
    poolA.close()
    print(f"[{os.getpid()} - INFO]: Joining Pool A!")
    poolA.join()
    print(f"[{os.getpid()} - INFO]: We called apply_async on Pool A, and was it successful? {arA.successful()}")
    print(f"[{os.getpid()} - INFO]: ================== Pool A - Silent Failures ========================== ")
    
    # Pool B - This would raise too
    # poolB = Pool(1)
    # poolB.map(work, [1])
    # print("Closing Pool B!")
    # poolB.close()
    # print("Joining Pool B!")
    # poolB.join()

    print(f"[{os.getpid()} - INFO]: Seems like everything went fine! Now, let's try an apply_async with an error callback!")

    # Pool C - raises, passed to error_callback, not lost
    print(f"[{os.getpid()} - INFO]: ================== Pool C - Errors Handled ========================== ")
    poolC = Pool(1)
    arC = poolC.apply_async(work_fail, callback=handle_result, error_callback=handle_error)
    print(f"[{os.getpid()} - INFO]: Closing Pool C!")
    poolC.close()
    print(f"[{os.getpid()} - INFO: Joining Pool C!")
    poolC.join()
    print(f"[{os.getpid()} - INFO]: We called apply_async on Pool B, and was it successful? {arC.successful()}")
    print(f"[{os.getpid()} - INFO]: ================== Pool C - Errors Handled ========================== ")


    print(f"[{os.getpid()} - INFO]: Seems like we got notified of an error! That's good! Now, let's try an apply_async with no inherent errors to show how it should work!")

    # Pool D - succeeds, nothing passed to error_callback, but is passed to handle_result

    print(f"[{os.getpid()} - INFO]: ================== Pool D - No Errors ========================== ")
    poolD = Pool(1)
    arD = poolD.apply_async(work_succeed, callback=handle_result, error_callback=handle_error)
    print(f"[{os.getpid()} - INFO]: Closing Pool D!")
    poolD.close()
    print(f"[{os.getpid()} - INFO]: Joining Pool D!")
    poolD.join()
    print(f"[{os.getpid()} - INFO]: We called apply_async on Pool B, and was it successful? {arD.successful()}")
    print(f"[{os.getpid()} - INFO]: ================== Pool D - No Errors ========================== ")
    
    print(f"[{os.getpid()} - INFO]: Main Thread, 'Successfully' exiting despite 2/3 of my child processes failing! Check my exit code with $? if you don't believe me!")

def work_fail():
    try:
        print(f"[{os.getpid()} - INFO]: There is no way that a divide by zero could ever NOT result in an exception, right!?")
        1/0
        print(f"[{os.getpid()} - INFO]: We should never see this log line so it's ok to put swear words in it, right!?")
    except Exception as ex:
        print(f"[{os.getpid()} -  ERR]: See? We 100 percent had a problem, and it was {ex}! Now, let's see if the error was handled...")
        raise ex # Rethrow it, just to prove it did exec, we did except, and still allow it to crash the child process silently

def work_succeed():
    try:
        print(f"[{os.getpid()} - INFO]: 1/1 will not raise an exception")
        1/1
        print(f"[{os.getpid()} - INFO]: 1/1 did not raise an exception")
    except Exception as ex:
        print(f"[{os.getpid()} -  ERR]: You'll never see an error like {ex} because it will not be raised!")
        raise ex # Rethrow it just in case, but it won't raise, so it doesn't matter


if __name__ == '__main__':
    main()