def assert_true_after_1_minute_max(assertion):
    from datetime import datetime
    from time import sleep

    start = datetime.now()
    while (datetime.now() - start).seconds < 60:
        sleep(0.1)  # Limit CPU usage
        try:
            if assertion():
                return
        except Exception as e:
            print("Raise (test_scheduler):", e)
    assert assertion()
