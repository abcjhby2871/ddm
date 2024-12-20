import pandas as pd
import matplotlib.pyplot as plt
import hddm
import kabuki
import arviz as az
import seaborn as sns
import warnings
import sys 
import os
import argparse
if not sys.warnoptions:
    warnings.simplefilter("ignore")

def main(args):
    prefix='/home/jovyan'
    sample_num=int(args.sample_num)
    burn_num=sample_num//2
    version=int(args.ve)
    user=f'{args.user}/v{version}'
    chains_num=2
    id=args.id
    data = hddm.load_csv(f'{prefix}/data/exp{id}.csv')
    data = hddm.utils.flip_errors(data)
    os.makedirs(f'{prefix}/{user}',exist_ok=True)
    if version==1:
        kwargs={
            "models":["v~dif+C( Third,Treatment('mid'))*C(Info, Treatment('MV'))","a~C(Third, Treatment('mid'))*C(Info, Treatment('MV'))"],
            "include":('v','a','t')
        }
    elif version==2:
        kwargs={
            "models":["v~dif*C(Third, Treatment('mid'))*C(Info, Treatment('MV'))","a~C(Third, Treatment('mid'))*C(Info, Treatment('MV'))"],
            "include":('v','a','t')
        }
        include=('v','a','t')
    elif version==3:
        kwargs={"models":["v~dif+C( Third,Treatment('mid'))*C(Info, Treatment('MV'))"],
               "include":('v','t')}
    else:
        raise NotImplementedError
    kwargs["p_outlier"]=0.05
    kwargs["group_only_regressors"]=False
    print(f'exp:{id},version:{version},path:{prefix}/{user},sample_num:{sample_num},burn_num:{burn_num},chain_num:{chains_num},kwargs:{kwargs}')
    
    pwd=os.getcwd()
    os.chdir(f'{prefix}/{user}')
    model = hddm.HDDMRegressor(data,**kwargs)
    rc = model.sample(sample_num,chains=chains_num, burn=burn_num,dbname=f'{prefix}/work/exp_{id}_v{version}.db',db='pickle',return_infdata=True, sample_prior=True, loglike=True, ppc=True)
    model.save(f'{prefix}/{user}/exp_{id}_v{version}')
    az.to_netcdf(rc, f'{prefix}/{user}/exp_{id}_v{version}.nc')
    os.chdir(pwd)
if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('user')
    parser.add_argument('id')
    parser.add_argument('--ve',default=2)
    parser.add_argument('--sample_num',default=10000)
    args=parser.parse_args()
    main(args)