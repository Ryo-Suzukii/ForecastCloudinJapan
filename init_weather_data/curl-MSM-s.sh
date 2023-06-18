mkdir data
cd data

for i in `seq 2022 2022`; do
  mkdir $i
  cd $i
  for j in `seq -w 1 12`; do
    mkdir $j
    cd $j
    for k in `seq -w 1 31`; do
      year=$i
      month=$j
      day=$k

      if [ ! -f "${year}_${month}${day}.nc" ]; then
        curl "http://database.rish.kyoto-u.ac.jp/arch/jmadata/data/gpv/netcdf/MSM-S/$year/$month$day.nc" -o ${year}_${month}${day}.nc
        echo "download ${year}_${month}${day}.nc"
      else
        echo "skip ${year}_${month}${day}.nc"
      fi
    done
    cd ../
  done
  cd ../
done
cd ../
