import re

def recip_rhythm(tune):

  melody = [line.rstrip() for line in open(tune, "r+")]
  ## define some empty lists that we might need later.
  x = []
  y = []

  ## for every line in the melody, if there is no !, =, or *, print the line.
  ## this gets rid of metadata and barlines. It puts everything into the
  ## x list.

  for f in melody:
    if "!" not in f and "=" not in f and "*" not in f:
      x.append(re.sub("[^0-9._\]\[]", "", f))

  for i in x:
    if "." not in i:
      i = float(i)
      recip = 1/i
      y.append(recip)

    else:
      no_dot = re.sub("\.", "", i)
      no_dot = float(no_dot)
      recip = (1/no_dot)+((1/no_dot)*.5)
      y.append(recip)

  return(y)


def npvi(tune):
  rhythm = recip_rhythm(tune)
  mel_length = 100/(len(rhythm) - 1)
  total = [abs(rhythm[onset] - (rhythm[onset+1])/(rhythm[onset] + (rhythm[onset+1]/2))) for onset in range(len(rhythm)-1)]
  total_sum = sum(total)
  answer = (mel_length * total_sum)
  return([tune, answer])