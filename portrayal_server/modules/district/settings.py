WANGGOU = ['Cmengbasha','Ctebu','Cmaibaobao','Cshitaibo','Ckuaile','Cyibaojian','Csanjia','Caigou','Caimu','Cleyier','Ctommy','Cyueji','Cshangtoushe','Cnop','Cpupai','Cjustyle','Csopool','Cyounandu','Czgppwh','CUA','Ctaipingniao','Cmasamasuo','Clanmiu','Clinghaonan','Csanfu','Cshikai','Cshanmaihuwai','Ctiexuejunpinxing','Cchangyou','Cliwaiyougou','Caijiaju','Cdapu','Cmeifenmeike','Cmili','Cmeiritongfan','Cpba','Czhiwo','Cxiaozhuang','Caiyingshi','Cmuyingzhijia','Chaohaizi','Cdbxsz','Caiyibeili','Clvhezhi','Canjuke_haozu','Chongjiuke','Cpingshanghongjiu','Ctengbangguoji','Ctianxiafenghuang','Czhongguoguolv','Clvmama','Cdiwudadao','Cqiaowuqiaoyu','Czouxiu','Cymall','Cshehuajie','Cyishang','Cshejisheji','Cleshang','Czhenpin','Cdushipiaowu','Ckadang','Cxipin','Ctuotuogs','Cbenlai','Cmaicha','Claiyifen','Chaishangwang','Cxiyuhongjiu','Czglingshi','Chaojiu','Cwolikuaigou','Czhengdatiandi','Cjiashiyi','Cqianfenzhiyi','Cgongtianxia','Cfuwa','Cliufangmushuguo','Cweifengshangcheng','Chaiershangcheng','Cgaohongshangcheng','Cfangzhengdianqi','Chaierguanwang','Cxin7tian','Czhizhuwang','Ckuaishubao','Cyidu','Cyouyi','Cmaibuxie','Cbaobaoshu','Cfanou','Chaolemai','Cmaimaixie','Chutaojiazi','Ctaoxie','Cpaixie','Cjiankangren','Cqicha','Ckaixinren','Cbjyaopin','Chaiwang','Cdaoyao','C818yiyao','Cqilekang','Cbaiyangjiankang','Cjianyi','C99kangti','Chuolida','Chuatuoyaofang','Caiduzhubao','Cyihaodian','Cyinzuo','Cwangfujing','Cwasai','Clianchi','Ctaochangzhou','Cyoupin','Cenvieshop','Cyintai','Czhongguoyidong','Ctaoluohe','Cxihuojie','Cweiwei','Cbailian','Cettshop','Cjiapin','Cjushang', 'Cosa', 'Czhongguanchun_shop', 'Cleju_keerrui', 'Cjumeiyoupin', 'Cyiyaowang', 'Ctiantianwang', 'Cguopi', 'Ctuangouwang']
TUAN = ['Cxiutuan', 'C58tuan', 'Cmanzuo', 'Cjinshan', 'Cdida', 'Cqingtuanwang', 'Clike', 'Cjuyue', 'Cqinqinwang', 'Cmangguo', 'C360tuan', 'Czhunawang', 'Cpinzhituan', 'Caipintuan']

HUAZHUANGPIN = ['Czhiwo', 'Cjumeiyoupin', 'Cmaibaobao', 'Cyiyaowang', 'Cwangfujing', 'Ctiantianwang', 'Cxiaozhuang', 'Cguopi']
TRAVEL = ['Clvmama', 'Czhunawang']
CLOTHES = ['Cyihaodian']

INDUSTRY = {
'1': TUAN,
'2': [], # jiadian
'3': HUAZHUANGPIN,
'4': TRAVEL,
'5': [], # wine
'6': ['Cyihaodian'],
}

INDUSTRY_MAP = {}
for k, v in INDUSTRY.iteritems():
    for cid in v:
        INDUSTRY_MAP[cid] = int(k)

CRAWL_WANGGOU = ['Cmangguo']
CRAWL_TUAN = ['C58tuan']
# 1: google coord, 0: baidu coord
FETCH_DISTRICT = {'Cjinshan': 1, 'Cdida': 1, 'Cmanzuo': 1, 'Ctengbangguoji': 0, 'Clike': 1, 'C58tuan': 1, 'Cqingtuanwang': 1, 'Cpinzhituan': 1, 'Cmangguo': 1, 'C360tuan': 1, 'Czhunawang': 0, 'Czhunawang': 0, 'Cleju_keerrui': 0, 'Caipintuan': 1}
