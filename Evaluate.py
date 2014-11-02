import MachineLearning.ML_Tools.log
import MachineLearning.ML_Tools.sigmond
import DataManager.GetRepoInfo
import Get_Model
import config

def get_repo_info(repo_name):
     repo_dic={}
     repo_dic=DataManager.GetRepoInfo.GetRepoInfo(repo_name)
     repo_dic=MachineLearning.ML_Tools.log.loge(repo_dic)
     return repo_dic

def evaluate(repo_name):
	dic_model=Get_Model.get_model()
	dic_target=get_repo_info(repo_name)
	factor=dic_model['constant'] 
	for i in config.feat:
	   if i =='name':
	    continue
	   else:  	
		factor=factor+dic_model[i]*dic_target[i]
	return factor

def get_score(repo_name):
     ful_name='https://api.github.com/repos/'+repo_name
     return (MachineLearning.ML_Tools.sigmond.sig((evaluate(ful_name))))*100



print get_score('jimenbian/DataMining')
