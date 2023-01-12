year=$1
month=$2

mkdir data
cd data
mkdir $year
cd $year
mkdir $month
cd $month

for j in {01..31}; do
    curl -O "http://database.rish.kyoto-u.ac.jp/arch/jmadata/data/gpv/netcdf/MSM-S/$year/$month$j.nc"
done
