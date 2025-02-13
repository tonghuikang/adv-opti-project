#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os, collections

import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.collections as mc

MAIN = __name__ == "__main__"


# # Parse Timetable

# In[2]:


def load_original_timetable(filepath):
    # wrt v5, rename original_day_ix and original_hour_ix
    df = pd.read_csv(filepath, dtype={'subject': str})
    
    df["day_ix"] = df["original_day_ix"]
    df["hour_ix"] = df["original_hour_ix"]
    
    assert "subject" in df.columns
    assert "class_num" in df.columns
    assert "proc_time" in df.columns
    assert "venue" in df.columns    
    return df

def make_records(df, idx_col):
    idxs = df[idx_col]
    record_list = df.to_dict('records')
    return {k:v for k,v in zip(idxs, record_list)}


# In[3]:


df_ref_job = load_original_timetable("./reference/TT Data.csv")
ref_job = make_records(df_ref_job, "job_ix")
# ref_instructor = make_records(pd.read_csv("./reference/reference - instructor.csv").fillna(0), "subject_ix")
ref_subject = make_records(pd.read_csv("./reference/reference - subject.csv").fillna(0), "subject_ix")
ref_venue = make_records(pd.read_csv("./reference/reference - venue.csv"), "venue_ix")
ref_time = make_records(pd.read_csv("./reference/reference - time.csv"), "time_ix")
df_ref_job


# In[4]:


# extrack track subjects
track_subjects = collections.defaultdict(set)

for subject_info in ref_subject.values():
    subject, subject_ix, *tracks = subject_info
    for track in tracks:
        if subject_info[track]:
            track_subjects[track].add(subject_info[subject])

track_color = {}
for subject in track_subjects['track_fin']:
    track_color[subject] = 'limegreen'
for subject in track_subjects['track_ba']:
    track_color[subject] = 'lightcoral'
for subject in track_subjects['track_avi']:
    track_color[subject] = 'deepskyblue'

track_subjects


# In[5]:


track_color


# In[6]:


# define blocked out timings
blocked_timings = [
    [("HASS", 15, 18)],
    [("HASS", 8.5, 10)],
    [("Capstone / End of Day", 13.5, 20)],
    [("HASS", 15, 18)],
    [("HASS", 11.5, 13.5), ("Capstone / End of Day", 13.5, 20)],
]


# # Extract subset
# We will only plot a subset of the timetable

# In[7]:


df_sample = df_ref_job[(df_ref_job["term"] == "ESD T5")&(df_ref_job["term_half"] == 1)]
df_sample = df_sample[["subject", "class_num", "venue", "day_ix", "hour_ix", "proc_time", "instructor"]]
df_sample


# # Plot timetable

# In[8]:


def organize_timetable(df, post_process_times=True):
    # organise the classes on each days to separate rows if overlapping, for visualisation
    # "subject", "class_code", "venue", "day_ix", "hour_ix", "proc_time"
    df = df.copy()
    
    if post_process_times:
        df["day_index"] = df["day_ix"]-1
        df["hour_index"] = df["hour_ix"]
        df["proc_time"] = df["proc_time"]/2
    
    records = df.to_dict('records')
    records = sorted(records, key=lambda x:(x["day_index"],x["hour_index"],x["proc_time"]))

    timetable = [[[]] for _ in range(5)]

    for record in records:
        pidx = 0  # parallel index
        while True:
            if timetable[record["day_index"]][pidx] == []:
                timetable[record["day_index"]][pidx].append(record)
                timetable[record["day_index"]].append([])
                break
            if timetable[record["day_index"]][pidx][-1]["hour_index"]              + timetable[record["day_index"]][pidx][-1]["proc_time"] <= record["hour_index"]:
                timetable[record["day_index"]][pidx].append(record)
                break
            pidx += 1
    
    timetable = [parallels[:-1] for parallels in timetable]
    return timetable

if MAIN:
    organized_timetable = organize_timetable(df_sample)
    # organized_timetable[0]


# In[9]:


def plot_organised_timetable(organized_timetable, save_path="", show_fig=False, 
                             title="", highlighted_track="", highlight_all_tracks=True):

    fig = plt.figure(figsize=(14,8), facecolor=(1, 1, 1))
    ax = plt.gca()

    def add_rectangle(ax, locx, locy, height, width, color="white"):
        ax.add_patch(patches.Rectangle((locx, locy), height, width, edgecolor="black",
                                       facecolor=color, alpha=0.5))

    def add_text(ax, locx, locy, text, offset=0.08):
        locx += offset
        locy += offset
        ax.text(locx, locy, text, verticalalignment='top', size='smaller')

    def add_horizontal_line(ax, y_intercept):
        ax.axhline(y_intercept)

    yptr = 1
    days_label_yptr = []
    add_horizontal_line(ax, 0.5)
    for idx,day_schedule in enumerate(organized_timetable):
        day_start_yptr = yptr
        for parallel_day_schedule in day_schedule:
            for record in parallel_day_schedule:
                xptr = record["hour_index"]
                width = record["proc_time"]
                color = "white"
                if record["subject"] in track_subjects[highlighted_track] or highlight_all_tracks:
                    if record["subject"] in track_color:
                        color = track_color[record["subject"]]
                    else:
                        if record["class_num"] == "CS01":
                            color = "yellow"
                        else:
                            color = "orange"
                add_rectangle(ax, xptr, yptr, width, 1, color=color)
                add_text(ax, xptr, yptr, record["subject"] + " " + record["class_num"])
                add_text(ax, xptr, yptr+0.3, record["venue"])
                add_text(ax, xptr, yptr+0.6, record["instructor"])
            yptr += 1
        day_end_yptr = yptr
        days_label_yptr.append((day_end_yptr + day_start_yptr)/2)
        add_horizontal_line(ax, yptr+0.5)
        
        for reason, start, end in blocked_timings[idx]:
            add_rectangle(ax, start, day_start_yptr, end-start, day_end_yptr-day_start_yptr, color="grey")
            add_text(ax, start, day_start_yptr, reason)
        
        yptr += 1

    day_code_to_day_index = {time["day"]:time["day_ix"]-1 for time in ref_time.values()}
    time_hour_to_hour_index = {time["hour_ix"]:time["hour"] for time in ref_time.values()}
    days_label = sorted(day_code_to_day_index, key=lambda x: day_code_to_day_index[x])
    
    plt.xlabel("Time")
    plt.xticks(*list(zip(*time_hour_to_hour_index.items())), rotation=30)
    plt.yticks(days_label_yptr, days_label)
    plt.xlim(16/2,41/2)
    plt.ylim(0.5,yptr-0.5)
    plt.title(title)
    ax.invert_yaxis()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
    if show_fig:
        plt.show()
    plt.close()


# # Term 5 timetable

# In[10]:


if MAIN:
    df_sample = df_ref_job[(df_ref_job["term"] == "ESD T5")&(df_ref_job["term_half"] == 1)]
    organized_timetable = organize_timetable(df_sample)
    plot_organised_timetable(organized_timetable, show_fig=True)


# # Term 7 timetable

# In[11]:


if MAIN:
    df_sample = df_ref_job[(df_ref_job["term"] != "ESD T5")&(df_ref_job["term_half"] == 1)]
    organized_timetable = organize_timetable(df_sample)
    plot_organised_timetable(organized_timetable, show_fig=True)


# # Plot all relevant timetables

# In[12]:


def analyse_related_features(df_output, folder_output="./", title_prefix=""):
    if not os.path.exists(folder_output):  # create folder if does not exist
        os.makedirs(folder_output)

    organized_timetable = organize_timetable(df_output)
    plot_organised_timetable(organized_timetable,
                             title="{}Complete Timetable".format(title_prefix),
                             save_path="{}/all.svg".format(folder_output))

    # term 5 timetable
    df_subset = df_output[df_output["term"] == "ESD T5"]
    organized_timetable = organize_timetable(df_subset)
    plot_organised_timetable(organized_timetable, 
                             title="{}Term 5 ESD modules".format(title_prefix),
                             save_path="{}/comb-ESD-T5.svg".format(folder_output))

    # term 5 cohort 1 timetable
    df_cohort = df_subset[(df_subset["class_num"] == "CS01") | (df_subset["class_num"] == "LS01")]
    organized_timetable = organize_timetable(df_cohort)
    plot_organised_timetable(organized_timetable, 
                             title="{}Term 5 ESD modules - cohort 1".format(title_prefix),
                             save_path="{}/comb-ESD-T5-cohort-1.svg".format(folder_output))

    # term 5 cohort 2 timetable
    df_cohort = df_subset[(df_subset["class_num"] == "CS02") | (df_subset["class_num"] == "LS01")]
    organized_timetable = organize_timetable(df_cohort)
    plot_organised_timetable(organized_timetable, 
                             title="{}Term 5 ESD modules - cohort 2".format(title_prefix),
                             save_path="{}/comb-ESD-T5-cohort-2.svg".format(folder_output))

    # term 7 timetable
    df_subset = df_output[df_output["term"] != "ESD T5"]
    organized_timetable = organize_timetable(df_subset)
    plot_organised_timetable(organized_timetable, 
                             title="{}Term 7 ESD modules".format(title_prefix),
                             save_path="{}/comb-ESD-T7.svg".format(folder_output))
    
    # plotting for each track
    for track in track_subjects:
        if track == "" or track == "track_core":
            continue
        plot_organised_timetable(organized_timetable, highlighted_track=track,
                                 title="{}Term 7 ESD modules - Track: {}".format(title_prefix, track), 
                                 save_path="{}/comb-ESD-T7-track-{}.svg".format(folder_output, track),
                                 highlight_all_tracks=False)
    
    # plotting for each instructor, venue, subject concerned
    for instructor in set(df_output["instructor"]):
        df_subset = df_output[df_output["instructor"] == instructor]  
        organized_timetable = organize_timetable(df_subset)
        plot_organised_timetable(organized_timetable, 
                                 title="{}For instructor {}".format(title_prefix, instructor),
                                 save_path="{}/instructor-{}.svg".format(folder_output, instructor))
    
    for venue in set(df_output["venue"]):
        for sub_venue in venue.split("/"):
            df_subset = df_output[df_output["venue"].str.contains(sub_venue)]
            organized_timetable = organize_timetable(df_subset)
            plot_organised_timetable(organized_timetable, 
                                     title="{}For venue {}".format(title_prefix, venue),
                                     save_path="{}/venue-{}.svg".format(folder_output, sub_venue))
    
    for subject in set(df_output["subject"]):
        df_subset = df_output[df_output["subject"] == subject]
        organized_timetable = organize_timetable(df_subset)
        plot_organised_timetable(organized_timetable, 
                                 title="{}For subject {}".format(title_prefix, subject),
                                 save_path="{}/subject-{}.svg".format(folder_output, subject))


# In[ ]:


if MAIN:
    df_output = df_ref_job[df_ref_job["term_half"] == 1]
    organized_timetable = organize_timetable(df_output)
    plot_organised_timetable(organized_timetable, show_fig=True)  # show master
    analyse_related_features(df_output, folder_output="./first-half/given-timetable",
                             title_prefix="Given Timetable - First Half - ")


# In[ ]:


if MAIN:
    df_output = df_ref_job[df_ref_job["term_half"] == 2]
    organized_timetable = organize_timetable(df_output)
    plot_organised_timetable(organized_timetable, show_fig=True)  # show master
    analyse_related_features(df_output, folder_output="./second-half/given-timetable",
                             title_prefix="Given Timetable - Second Half - ")


# # Parsing a sample result

# In[ ]:


results = '''
X[1,26,29] 1
X[2,26,49] 1
X[3,26,34] 1
X[4,26,67] 1
X[5,26,1] 1
X[6,26,44] 1
X[7,33,9] 1
X[8,33,50] 1
X[9,33,79] 1
X[10,32,9] 1
X[12,32,1] 1
X[13,32,29] 1
X[27,20,1] 1
X[28,20,44] 1
X[29,17,29] 1
X[30,17,59] 1
X[31,12,86] 1
X[32,32,5] 1
X[33,6,49] 1
X[34,6,1] 1
X[35,6,83] 1
X[36,1,35] 1
X[37,12,1] 1
X[38,12,36] 1
X[40,17,37] 1
X[54,17,41] 1
X[55,17,67] 1
X[56,21,67] 1
X[57,21,84] 1
'''.strip()
results = [list(map(int,result.split("]")[0].split("[")[1].split(','))) for result in results.split('\n')]
results # job_ix, venue_ix, time_ix


# In[ ]:


def parse_results(results):
    records = []
    for job_ix, venue_ix, time_ix in results:
        venue = ref_venue[venue_ix]
        time = ref_time[time_ix]
        job = ref_job[job_ix]
        record = {
            "day_ix": time["day_ix"],
            "hour_ix": time["hour_ix"],
            "proc_time": job["proc_time"],
            "venue": venue["venue"],
            "class_num": job["class_num"],
            "subject": job["subject"],
            "instructor": job["instructor"],
            "term": job["term"]
        }
        records.append(record)
    return pd.DataFrame.from_records(records)


# In[ ]:


if MAIN:
    df_output = parse_results(results)
    organized_timetable = organize_timetable(df_output)
    plot_organised_timetable(organized_timetable, show_fig=True)  # show master
    analyse_related_features(df_output, folder_output="sample-parsed-timetable", 
                             title_prefix="Sample Parsed Timetable - ")


# (for versioning purposes)

# In[ ]:


if MAIN:
    get_ipython().system('jupyter nbconvert --to script viz.ipynb')


# In[ ]:




