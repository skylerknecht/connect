function sleep(tmp){
  if (tmp < 100){
    return 'Please provide a value of atleast 100 milliseconds.';
  }
  {{ variables['sleep'][0] }} = tmp;
  return 'Successfully changed checkin time.';
}
