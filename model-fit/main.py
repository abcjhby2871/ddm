import pandas as pd
import matplotlib.pyplot as plt
import hddm
import kabuki
import arviz as az
import seaborn as sns
import warnings
import sys 
import argparse
if not sys.warnoptions:
    warnings.simplefilter("ignore")

def main(args):
    prefix='/home/jovyan'
    user=args.user
    sample_num=int(args.sample_num)
    burn_num=sample_num//2
    version=int(args.ve)
    chains_num=2
    id=args.id
    print(f'exp:{id},version:{version},sample_num:{sample_num},burn_num:{burn_num},chain_num:{chains_num}')
    data = hddm.load_csv(f'{prefix}/data/exp{id}.csv')
    data = hddm.utils.flip_errors(data)
    if version==1:
        v_func=["v~dif+C( Third,Treatment('mid'))*C(Info, Treatment('MV'))","a~C(Third, Treatment('mid'))*C(Info, Treatment('MV'))"]
    elif version==2:
        v_func=["v~dif*C(Third, Treatment('mid'))*C(Info, Treatment('MV'))","a~C(Third, Treatment('mid'))*C(Info, Treatment('MV'))"]
    else:
        raise NotImplementedError
    model = hddm.HDDMRegressor(data, ["v~dif*C(Third, Treatment('mid'))*C(Info, Treatment('MV'))","a~C(Third, Treatment('mid'))*C(Info, Treatment('MV'))"],
                             p_outlier=0.05,
                             group_only_regressors = False,
                             include = ('v','a','t'))
    rc = model.sample(sample_num,chains=chains_num, burn=burn_num,dbname=f'{prefix}/{user}/exp_{id}_v{version}.db',db='pickle',return_infdata=True, sample_prior=True, loglike=True, ppc=True)
    model.save(f'{prefix}/{user}/exp_{id}_v{version}')
    az.to_netcdf(rc, f'{prefix}/{user}/exp_{id}_v{version}.nc')
if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('id')
    parser.add_argument('--user','.')
    parser.add_argument('--ve',default=2)
    parser.add_argument('--sample_num',default=10000)
    args=parser.parse_args()
    main(args)