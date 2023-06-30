from datetime import datetime
import pandas as pd

class Getmaster:
    """ame_masterより雪番号があるかシノップ番号が5桁以上(登録されている)のどっちかがあるアメダスの情報を抜き出す関数
    """
    def __init__(self) -> None:
        self.master_df = pd.read_csv("ame_master_20230323.csv").rename(columns={"観測所名":"station"})
        self.list_df = pd.read_csv("amedas_url_list2.csv")
        self.amedas_snow = self._focus(self.master_df,self.list_df)
    
    def _focus(self,master_df,list_df):
        """実際に抽出する関数。内部でしか使わない

        Args:
            master_df (pd.DataFrame): ame_masterの情報を格納したDataFrame
            list_df (pd.DataFrame): 気象庁過去データのurlを格納したDataFrame

        Returns:
            pd.DataFrame: 抽出したDataFrame.Columns["station","amedas_id","snow","block_id"]
        """
        
        list_df["block_id"] = list_df["amedas_url"].apply(lambda x: (x.split("&")[1].split("=")[1]))
        
                            ### WARNING ####
        ### 観測所名でmergeしてるからpandasの仕様上存在しない観測所が生まれる ###
        ### scrape.pyでエラーログ出力された所はこのせい ###
        
        all_df = pd.merge(master_df,list_df,on="station")
        all_df["block_id"] = all_df["block_id"].astype(int)
        amedas_df = all_df[["station","観測所番号","備考1","block_id"]]
        amedas_snow = amedas_df[(amedas_df["block_id"] > 9999) | (amedas_df["備考1"] != "－")]
        amedas_snow = amedas_snow.rename(columns={"観測所番号":"amedas_id","備考1":"snow"})
        return amedas_snow
    
    def getter(self):
        return self.amedas_snow
    
def main():
    Getmaster()

if __name__ == "__main__":
    main()