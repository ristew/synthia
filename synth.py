import os, math, random, struct, sys

def expnote(n):
    """get a note freq relative to low A"""
    return 440.0 * 2.0**n 

ns = [i / 13 for i in range(13)]
scale_nums = [0, 2, 4, 5, 7, 9, 11, 12]
# AMaj
scale = [expnote(ns[i]) for i in scale_nums]
SAMPLE_RATE = 22050
TRIANGLE, SQUARE, SAWTOOTH, SINE = 1, 2, 3, 4

class SongMan(object):
    """a Song Man plays songs"""
    def __init__(self, rate, wavetype=SAWTOOTH, attackt=1.5, decayt=1.2, releaset=3.0, susv=0.75):
        self.rate = rate
        self.curtime = 0.0
        self.music = []
        self.wavetype = wavetype
        # adsr parameters
        self.attackt = attackt
        self.decayt = decayt
        self.releaset = releaset
        self.susv = susv

    def note(self, hz):
        return self.rate / (2 * math.pi * max(hz, 1) )

    def adsr(self, time, vol):
        vols = []
        curv = 0.0
        tottimes = int(time * self.rate)
        for i in range(tottimes):
            # attack
            if i < self.attackt * self.rate:
                curv += vol / (self.attackt * self.rate)
            # decay
            elif i < (self.attackt + self.decayt) * self.rate:
                curv -= (1.0 - self.susv) * vol / (self.decayt * self.rate)
            vols.append(curv)
        for i in range(int(self.releaset * self.rate)):
            # release
            curv -= self.susv * vol / (self.releaset * self.rate)
            vols.append(curv)
            
        return vols

    def play_note(self, hz, vol, dur, time):
        """play a note with frequency hz at amplitude vol dur seconds at time in the song"""
        tottimes = int(dur * self.rate)
        # generate ADSR envelope
        envel = self.adsr(dur, vol)
        cycle = int(time * self.rate)
        
        if self.wavetype == SAWTOOTH:
            harms = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        elif self.wavetype == SINE:
            harms = [1]
        else:
            harms = [1, 3, 5, 7, 9, 11, 13]
        for vol in envel:
            note = 0.0
            for harm in harms:
                if self.wavetype == TRIANGLE:
                    harm = harm**2
                note += 1.0 / harm * vol * math.sin(cycle / self.note(harm * hz))
            if cycle < len(self.music):
                self.music[cycle] = self.music[cycle] + note
            else:
                self.music.append(note)
            cycle += 1

    def add_note(self, hz, vol, dur):
        self.play_note(hz, vol, dur, self.curtime)
        self.curtime += dur
    
    def write_file(self, fname):
        import scipy.io.wavfile as wav, numpy as np
        wav.write(fname, self.rate, np.array(self.music))

    def play(self):
        import pyaudio
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32,
                        channels=1,
                        rate=SAMPLE_RATE,
                        output=True)
        stream.write(struct.pack('%sf' % len(sm.music), *sm.music))
        stream.stop_stream()
        stream.close()
        p.terminate()

sm = SongMan(SAMPLE_RATE, wavetype=SAWTOOTH)
sm.play_note(scale[0], 0.3, 3.6, 0.5)
sm.play_note(scale[2], 0.3, 3.3, 0.8)
sm.play_note(scale[4], 0.3, 3.0, 1.1)
sm.play()
sm.write_file("test.wav")
