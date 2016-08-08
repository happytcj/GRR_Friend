
# coding: utf-8

# In[1]:

get_ipython().magic(u'load_ext autoreload')
get_ipython().magic(u'autoreload 2')

from enumerate_datasets import *
from import_csv import *


# In[2]:

dataset_paths = enumerate_datasets('.')
print('%d datasets found' %len(dataset_paths))


# In[3]:

for path in dataset_paths:
    import_csv(path)


# In[4]:

def cursor_for_filter(path, filter):
    con = sqlite3.connect(path.replace('.csv', '.db'))
    c = con.cursor()
    c.execute(filter)
    return c


# In[5]:

accumulator = 0;
count = 0;


# In[6]:

def reset_gvars():
    global accumulator
    accumulator = 0;
    global count
    count = 0;


# In[7]:

#calculate grand mean

for path in dataset_paths:
    print path
    c = cursor_for_filter(path, """SELECT result FROM data""")
    for value in c.fetchall():
        accumulator += value[0]
        count += 1

gm = accumulator / count
print ('grand mean is %f' %gm)


# In[8]:

#calculate same OP means
reset_gvars()
opm = []

for idx, path in enumerate(dataset_paths):
    c = cursor_for_filter(path, """SELECT result FROM data""")

    for value in c.fetchall():
        accumulator += value[0]
        count += 1

    opm.append(accumulator / count) 
    print ('op mean is %f' %opm[-1])
    reset_gvars()


# In[9]:

#calculate mean for same part ID; need to query across dbs
reset_gvars()
snm = []

c = cursor_for_filter(dataset_paths[0], """select distinct sn, count(sn) as CountOf from data group by sn""")
sns = c.fetchall()
num_sn = len(sns)

for sn in sns:
    for idx, path in enumerate(dataset_paths):
        c = cursor_for_filter(path, """select result from data where sn = %s""" %sn[0])
        for value in c.fetchall():
            accumulator += value[0]
            count += 1
    snm.append(accumulator / count)
    reset_gvars()

print snm


# In[10]:

'''calculate mean for the same function: 
all measurements with the same part and operator ID’s;
represents repeatability.'''
reset_gvars()
fm = []
fm_lin = []
fm_part = []

for path in dataset_paths:
    
    for sn in sns:
        c = cursor_for_filter(path, """select result from data where sn = %s""" %sn[0])
        for value in c.fetchall():
            accumulator += value[0]
            count += 1
        mean = accumulator / count
        fm_part.append(mean)
        for i in range(len(dataset_paths)):
            fm_lin.append(mean)
        reset_gvars()
        
    fm.append(fm_part)
    fm_part = []
    reset_gvars()


# In[11]:

c = cursor_for_filter(path, """select COUNT(*) from data where sn = %s""" %sn[0])
num_tests = c.fetchone()[0]


# In[12]:

#calculate square difference btw means
def sd(x):
    return pow(x - gm, 2)

opsd = map(sd, opm)
snsd = map(sd, snm)


# In[13]:

def recursive_len(item):
    if type(item) == list:
        return sum(recursive_len(subitem) for subitem in item)
    else:
        return 1


# In[14]:

#read in all the values from every dataset
reset_gvars()
every_value = []
for path in dataset_paths:
    print path
    c = cursor_for_filter(path, """SELECT result FROM data""")
    for value in c.fetchall():
        every_value.append(value[0])
        
evsd = map(sd, every_value)


# In[15]:

idx = 0
fsd = []
for idx, value in enumerate(fm_lin):
    tmp = every_value[idx] - fm_lin[idx]
    fsd.append(pow(tmp,2))


# In[41]:

#sum each of the squared differences
def ss(x):
    return sum(x) * len(every_value) / len(x)

op_ss = ss(opsd)
sn_ss = ss(snsd)
ev_ss = ss(evsd)
rep_ss  = ss(fsd)


# In[42]:

sn_op_ss = ev_ss - f_ss - sn_ss - op_ss


# In[91]:

num_op = len(dataset_paths)

#calculate degrees of freedom
df_sn = num_sn - 1
df_op = num_op - 1
df_rep_no_int = num_sn * num_op  * (num_tests - 1)
df_total = num_sn * num_op * num_tests - 1
df_sn_op = (num_sn - 1) * (num_op - 1)


# In[92]:

#calculate mean squared difference for each factor
msd_op = op_ss / df_op
msd_sn = sn_ss / df_sn
msd_rep = rep_ss / df_rep
msd_sn_op = sn_op_ss / df_sn_op


# In[93]:

f_stat = msd_sn_op / msd_rep


# In[94]:

#calculate significance of part operator interaction
from scipy.stats import f
f_prob = 1 - f.cdf(f_stat, df_sn_op, df_rep)
alpha = 0.25


# In[101]:

#decide whether to include part operator interaction in the model
if f_prob > alpha:
    rep_ss = ev_ss - sn_ss - op_ss
    df_rep_int = df_rep_no_int + (df_op * df_sn)
    msd_rep = rep_ss / df_rep_int
    df_rep = df_rep_int
    op_sn_interaction = True
    print msd_rep
else:
    df_rep = df_rep_no_int
    op_sn_interaction = False


# In[111]:

#calculate variance components and stdevs
var_sn = max(0, (msd_sn-msd_rep) / (num_op*num_tests))
var_op = max(0, (msd_op-msd_rep) / (num_sn*num_tests))
var_repeatability = max(0, msd_rep)


# In[112]:

if not op_sn_interaction:
    var_sn_op = max(0, (msd_sn_op-msd_rep) / (num_tests))
else: 
    var_sn_op = 0
print var_sn_op


# In[110]:

if not op_sn_interaction:
    var_reproducibility = var_op
else: 
    var_reproducibility = var_op + var_sn_op
print var_reproducibility


# In[114]:

#calculate total GRR variance
var_GRR = var_reproducibility + var_repeatability
print var_GRR


# In[19]:

#define interface at this step


# In[ ]:



