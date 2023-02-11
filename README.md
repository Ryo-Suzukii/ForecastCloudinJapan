# Forcast Cloud in Japan
## ja-JA

### データのダウンロード方法
容量の問題よりgitでは追跡していないMSMデータと
### 雲量
気象庁が提供しているデータのうち雲量には`0+`や`10-`といった特殊な表記が存在する．
そもそもこれらの値が指し示す指標は以下のとおりである．
- `--`	該当現象、または該当現象による量等がない場合に表示します。
- `0`   該当現象による量はあるが、1に足りない場合に表示します。
- `0.0`	該当現象による量はあるが、0.1に足りない場合に表示します。ただし、降水量の場合は、0.5mmに足りない場合に0.0と表示します。
- `0+`	雲はあるが、雲量が1に満たない場合です。
- `10-`	雲量が10でも、雲がない部分がある場合です。

これらを数字として統一するためそれぞれ以下のとおりとする
- `np.nan` or `nan`
- `0`
- `0.05`
- `0.5`
- `9.5`

## en-EN

### Amout of Cloud
The Japan Meteorological Agency provides data on cloud coverage, which includes special notations such as 0+ and 10-. The following is what these values indicate:

- `--` indicates the absence of the relevant phenomenon or the relevant quantity.
- `0` indicates that there is a relevant quantity but it is not enough to reach 1.
- `0.0` indicates that there is a relevant quantity but it is not enough to reach 0.1. However, in the case of precipitation, it is indicated as 0.0 when it does not reach 0.5mm.
- `0+` indicates that there are clouds but the cloud coverage is not enough to reach 1.
- `10-` indicates that although the cloud coverage reaches 10, there are areas without clouds.
To unify these as numerical values, they are each treated as follows:

- `np.nan or nan`
- `0`
- `0.05`
- `0.5`
- `9.5`