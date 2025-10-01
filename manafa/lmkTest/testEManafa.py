import time

from manafa.emanafa import EManafa

manafa = EManafa()
input("please turn on project")
manafa.init()
manafa.start()
print("profiling...")
# wait function app done 
input("please turn of project")
print("stopping profiler...")
manafa.stop()
begin = manafa.perf_events.events[0].time  # first sample from perfetto
end = manafa.perf_events.events[-1].time  # last sample from perfetto
total, per_c, timeline = manafa.get_consumption_in_between(begin, end)

print(f"Total energy consumed: {total} Joules")
print(f"Elapsed time: {end - begin} secs")
print("--------------------------------------")
print("Per-component consumption")
print(per_c)
print("--------------------------------------")