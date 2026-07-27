# Recovery claim

The worker catches every exception and acknowledges the queue item in a `finally` block. No replay log, dead-letter path, checkpoint proof, reconciliation process, or incident exercise is supplied.
