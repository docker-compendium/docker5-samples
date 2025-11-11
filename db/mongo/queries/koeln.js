let cathedral = db.geoname.findOne({
  name: /Köln.*Dom/
});

const query = [
  {
    $geoNear: {
      near: cathedral.location,
      spherical: true,
      distanceField: 'dis',
      query: { feature_code: 'HTL' }
    }
  }, {
    $limit: 10
  }
];
let res = db.geoname.aggregate(query);
res.forEach(data => {
  print(Math.round(data.dis)+ "m: " + data.name);
});
