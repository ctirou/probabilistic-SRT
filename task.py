from psychopy import visual, core, event, gui, monitors, sound, parallel
from serial import Serial
# import pylink
# import EyeLink
import time
import shelve
import random
import codecs
import os
import pyglet
import platform
import numbers
from datetime import datetime
from io import StringIO
import threading
import os.path as op
import pandas as pd
import numpy as np


def serial_port(port='COM1', baudrate=9600, timeout=0):
    """
    Create serial port interface.

    str port: Which port to interface with.
    baudrate: Rate at which information is transferred in bits per second.
    int timeout: Waiting time in seconds for the port to respond.
    return: serial port interface
    """
    
    open_port = Serial(port, baudrate, timeout=timeout)
    open_port.close()
    open_port = Serial(port, baudrate, timeout=timeout)
    open_port.flush()
    return open_port


try:
    root = op.dirname(op.abspath(__file__))
except NameError:
    import sys
    root = op.dirname(op.abspath(sys.argv[0]))

def ensure_dir(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

def normalize_string(string, blank_char):
    string = string.lower()
    string = string.replace(' ', blank_char)
    return string


class ExperimentSettings:
    """
        This class handles all operation related to experiment settings.
        These settings apply to all subjects in the specific experiment.
    """    
    
    def __init__(self, settings_file_path, reminder_file_path, sequence_file_path):
        
        self.numsessions = 2 # number of sessions
        self.current_session = None # current session
        
        self.blocks_in_session = None 
        self.trials_in_tBlock = None
        self.trials_in_block = None
        
        self.monitor_width = None
        self.computer_name = None

        self.RSI_time = None # response-to-next-stimulus in milliseconds
        self.rest_time = None # resting period duration in seconds

        self.key1 = None
        self.key2 = None
        self.key3 = None
        self.key4 = None
        self.key_quit = None

        self.whether_warning = None
        self.speed_warning = None
        self.acc_warning = None
        
        self.sessionstarts = None
        self.blockstarts = None
        self.fb_block = None

        self.settings_file_path = settings_file_path
        self.reminder_file_path = reminder_file_path
        self.sequence_file_path = sequence_file_path

    def read_from_file(self):
        """Open settings shelve file in read-only mode and read all settings from it.

           This method expects that all known settings are in the file.
           If something is missing all read settings are dropped and also
           an exception is raised.
        """
                
        try:
            with shelve.open(self.settings_file_path, 'r') as settings_file:
                
                self.numsessions = settings_file['numsessions']
                
                self.blocks_in_session = settings_file['blocks_in_session']
                self.trials_in_tBlock = settings_file['trials_in_tBlock']
                self.trials_in_block = settings_file['trials_in_block']

                self.monitor_width = settings_file['monitor_width']
                self.computer_name = settings_file['computer_name']
                                
                self.RSI_time = settings_file['RSI_time']
                self.rest_time = settings_file['rest_time']

                self.key1 = settings_file['key1']
                self.key2 = settings_file['key2']
                self.key3 = settings_file['key3']
                self.key4 = settings_file['key4']
                self.key_quit = settings_file['key_quit']

                self.whether_warning = settings_file['whether_warning']
                self.speed_warning = settings_file['speed_warning']
                self.acc_warning = settings_file['acc_warning']
        
        except Exception as exception:
            self.__init__(self.settings_file_path, self.reminder_file_path, self.sequence_file_path)
            raise exception

    def write_to_file(self): 
        """Create a new settings file and write all settings into it."""
        
        with shelve.open(self.settings_file_path, 'n') as settings_file:
            settings_file['numsessions'] = self.numsessions
            
            settings_file['blocks_in_session'] = self.blocks_in_session
            settings_file['trials_in_tBlock'] = self.trials_in_tBlock
            settings_file['trial_in_block'] = self.trials_in_block

            settings_file['monitor_width'] = self.monitor_width
            settings_file['computer_name'] = self.computer_name
            
            settings_file['RSI_time'] = self.RSI_time
            settings_file['rest_time'] = self.rest_time

            settings_file['key1'] = self.key1
            settings_file['key2'] = self.key2
            settings_file['key3'] = self.key3
            settings_file['key4'] = self.key4
            settings_file['key_quit'] = self.key_quit

            settings_file['whether_warning'] = self.whether_warning
            settings_file['speed_warning'] = self.speed_warning
            settings_file['acc_warning'] = self.acc_warning

    def write_out_reminder(self):
        """Write out a short summary of the settings into a text file."""

        with codecs.open(self.reminder_file_path, 'w', encoding='utf-8') as reminder_file:
            reminder = str('Settings\n' +
                           '/n' + 
                           'Monitor Width: ' + '\t' + str(self.monitor_width).replace('.', ',') + '\n' +
                           'Computer Name: ' + '\t' + self.computer_name + '\n')
            
            reminder += str('Response keys: ' + '\t' + self.key1 + ', ' + self.key2 + ', ' + self.key3 + ', ' + self.key4 + '.' + '\n' +
                            'Quit key: ' + '\t' + self.key_quit + '\n' +
                            'Warning (speed, accuracy): ' + '\t' + str(self.whether_warning) + '\n' +
                            'Speed warning at:' + '\t' + str(self.speed_warning) + '\n' +
                            'Acc warning at:' + '\t' + str(self.acc_warning) + '\n')

            reminder += str('Sessions:' + '\t' + str(self.numsessions) + '\n' +
                            'Blocks per session: ' + '\t' + str(self.blocks_in_session) + '\n' +
                            'Training Trials\\Block:' + '\t' + str(self.trials_in_tBlock) + '\n' +
                            'Trials\\Block:' + '\t' + str(self.trials_in_block) + '\n' +
                            'RSI:' + '\t' + str(self.RSI_time).replace('.', ',') + '\n'
                            'Resting time: ' + '\t' + str(self.rest_time).replace('.', ',') + '\n')

            reminder += str('\n' +
                            'The following settings are valid and applies for all persons\n\n' +

                            'The settings apply to experiments that are created from this folder,\n' +
                            'started with the script found here. If you want to apply other settings,\n' +
                            'copy asrt.py and the inst_and_feedback.txt file containing the instructions to a\n' +
                            'to another directory, and you can enter the desired other settings when starting that script.\n\n' +

                            'Make sure that you always start the script from the directory where it is suitable for you\n' +
                            'settings are saved.\n\n' +

                            'The settings can be changed by deleting the settings/settings file; at the same time the file\n' +
                            'deletion is not recommended due to later transparency. If you still decide to delete,\n' +
                            'copy this .txt file beforehand so that you can remember the previous settings if necessary.\n')

            reminder_file.write(reminder)

    def maxtrial_traintest(self):
        """Get number of all trials per session, training included."""

        return self.trials_in_block * self.blocks_in_session + self.trials_in_tBlock
    
    def maxtrial_test(self):
        """Get number of all trials per session, training excluded."""

        return self.trials_in_block * self.blocks_in_session

    def get_block_starts(self):
        """Return with a list of numbers indicating the first trials of the different blocks."""

        if self.blockstarts == None:
            self.blockstarts = [1]
            for i in range(1, self.blocks_in_session + 2):
                self.blockstarts.append(i * (self.trials_in_block) + 1)
        
        return self.blockstarts
    
    def get_fb_block(self):
        """Returns with a list of numbers indicating when the feedback must be shown."""
        
        if self.fb_block == None:
            self.fb_block = []
            for i in range(1, self.maxtrial_traintest() + 2, 80):
                self.fb_block.append(i * (self.trials_in_block) + 1)
        
        return self.fb_block
 
    def get_session_starts(self):
        """Return with a list of numbers indicating the first trials of the different sessions."""

        if self.sessionstarts == None:
            self.sessionstarts = [1]
            epochs_cumulative = []
            session_no = 0
            e_temp = 0
            
            for e in range(self.blocks_in_session):
                e_temp += e
                session_no += 1
                epochs_cumulative.append(e_temp)

            for e in epochs_cumulative:
                self.sessionstarts.append(e * self.blocks_in_session * self.trials_in_block + 1)

            del self.sessionstarts[0]
            
        return self.sessionstarts

    def get_key_list(self):
        return (self.key1, self.key2, self.key3, self.key4, self.key_quit)

    def show_basic_settings_dialog(self):
        """ Ask the user to specify the number of groups and the number of sessions."""

        settings_dialog = gui.Dlg(title='Experiment design')
        settings_dialog.addText('No settings saved for this experiment yet...')
        settings_dialog.addField('Current session:', choices=['1st', '2nd'])
        settings_dialog.addField('Blocks per session', 160)
        settings_dialog.addField('Trials in training block', 40)
        settings_dialog.addField('Trials per testing block', 20)
        returned_data = settings_dialog.show()
        if settings_dialog.OK:
            if returned_data[0] == '1st':
                self.current_session = 1
            else:
                self.current_session = 2
            self.blocks_in_session = returned_data[1]
            self.trials_in_tBlock = returned_data[2]
            self.trials_in_block = returned_data[3]
        else:
            core.quit()

    def show_computer_and_display_settings_dialog(self):
        """Ask the user specific information about the computer and also change display settings."""

        settings_dialog = gui.Dlg(title='Settings')
        settings_dialog.addField('Monitor Width (cm)', 34.2)
        settings_dialog.addField('Computer name', 'local_cermep')
        settings_dialog.addField('RSI (ms)', 120)
        settings_dialog.addField('Resting time (s)', 5)

        returned_data = settings_dialog.show()
        
        if settings_dialog.OK:
            self.monitor_width = returned_data[0]
            self.computer_name = returned_data[1]
            self.RSI_time = float(returned_data[2]) / 1000
            self.rest_time = float(returned_data[3])

        else:
            core.quit()
        

    def show_key_and_feedback_settings_dialog(self):
        """Ask the user to specify the keys used during the experiement and also set options related to the displayed feedback."""

        settings_dialog = gui.Dlg(title='Settings')
        settings_dialog.addText('Answer keys')
        settings_dialog.addField('Up:', 'h')
        settings_dialog.addField('Left', 'j')
        settings_dialog.addField('Right', 'k')
        settings_dialog.addField('Down', 'l')
        settings_dialog.addField('Quit', 'q')
        settings_dialog.addField('Warning for accuracy/speed:', True)
        settings_dialog.addField('Warning for speed above this threshold (%):', 93)
        settings_dialog.addField('Warning accuracy below this threshold (%):', 91)
        returned_data = settings_dialog.show()
        if settings_dialog.OK:
            self.key1 = returned_data[0]
            self.key2 = returned_data[1]
            self.key3 = returned_data[2]
            self.key4 = returned_data[3]
            self.key_quit = returned_data[4]
            self.whether_warning = returned_data[5]
            self.speed_warning = returned_data[6]
            self.acc_warning = returned_data[7]
        else:
            core.quit()

    # def eyetrack_init(self, edfFileName):
    #     screen = pyglet.canvas.get_display().get_default_screen()
    #     selfEdf = EyeLink.tracker(screen.width, screen.height, edfFileName)
    #     EyeLink.tracker.sendMessage(selfEdf, 'H')
    #     EyeLink.tracker.close(selfEdf, edfFileName)


class InstructionHelper:
    
    def __init__(self, instructions_file_path):
        # instructions in the beginning of the experiment (might have more elements)
        self.insts = []
        # feedback for the subject about speed and accuracy in the implicit asrt case
        self.feedback_imp = []
        # message in the end of the experiment
        self.ending = []
        # shown message when continuing sessions after the previous data recoding was quited
        self.unexp_quit = []
        # shown message when the training has ended
        self.train_end = []

        self.instructions_file_path = instructions_file_path

    def read_insts_from_file(self):
        """Read instruction strings from the instruction file using the special structure of this file.
           Be aware of that line endings are preserved during reading instructions.
        """
        
        try:
            with codecs.open(self.instructions_file_path, 'r', encoding='utf-8') as inst_feedback:
                all_inst_feedback = inst_feedback.read().split('***')
        except:
            all_inst_feedback = []

        for all in all_inst_feedback:
            all = all.split('#')
            if len(all) >= 2:
                if 'inst' in all[0]:
                    self.insts.append(all[1])
                elif 'training' in all[0]:
                    self.train_end.append(all[1])
                elif 'feedback' in all[0]:
                    self.feedback_imp.append(all[1])
                elif 'ending' in all[0]:
                    self.ending.append(all[1])
                elif 'unexpected quit' in all[0]:
                    self.unexp_quit.append(all[1])
                            
    def validate_instructions(self, settings):
        """Do a minimal validation of the read instructions to get error messages early,
           before a missing string actualy causes an issue."""

        if len(self.insts) == 0:
            print("Starting instruction was not specified!")
            core.quit()
        if len(self.train_end) == 0:
            print("Training end message was not specified!")
            core.quit()
        if len(self.ending) == 0:
            print("Ending message was not specified!")
            core.quit()
        if len(self.unexp_quit) == 0:
            print("Unexpected quit message was not specified!")
            core.quit()
        if len(self.feedback_imp) == 0:
            print("Feedback message was not specified!")
            
    def __print_to_screen(self, mytext, mywindow):
        text_stim = visual.TextStim(mywindow, text=mytext,
                                    units='cm', height=0.8, wrapWidth=20, color='black')
        text_stim.draw()
        mywindow.flip()
    
    
    def __show_message(self, instruction_list, experiment):
        for inst in instruction_list:
            self.__print_to_screen(inst, experiment.mywindow)
            tempkey = event.waitKeys(keyList=experiment.settings.get_key_list())
            if experiment.settings.key_quit in tempkey:
                core.quit()
    
    def show_instructions(self, experiment):
        self.__show_message(self.insts, experiment)
    
    def show_training_end(self, experiment):
        self.__show_message(self.training_end, experiment)
    
    def show_unexp_quit(self, experiment):
        self.__show_message(self.unexp_quit, experiment)
        
    def show_ending(self, experiment):
        self.__show_message(self.show_ending, experiment)
    

    def feedback_RT_acc(self, rt_mean, rt_mean_str, acc_for_the_whole, acc_for_the_whole_str, mywindow, experiment_settings):
        """Display feedback screen in case of an implicit ASRT.

           The feedback string contains placeholders for reaction time and accuracy.
           Based on the settings the feedback might contain extra warning
           about the speed or accuray.
        """
        
        for i in self.feedback_imp:
            i = i.replace('*MEANRT*', rt_mean_str)
            i = i.replace('*PERCACC*', acc_for_the_whole_str)

            if experiment_settings.whether_warning is True:
                if rt_mean > experiment_settings.speed_warning:
                    i = i.replace('COMMENT', 'Soyez plus rapide !')
                elif acc_for_the_whole < experiment_settings.acc_warning:
                    i = i.replace('COMMENT', 'Soyez plus précis !')
                elif rt_mean > experiment_settings.speed_warning and acc_for_the_whole < experiment_settings.acc_warning:
                    i = i.replace('COMMENT', 'Soyez plus rapide et plus précis !')
                else:
                    i = i.replace('COMMENT', 'Continuez ainsi !')
            else:
                i = i.replace('COMMENT', '')
            
            self.__print_to_screen(i, mywindow)

class PersonDataHandler:
    """Class for handle subject related settings and data."""

    def __init__(self, subject_id, all_settings_file_path, all_IDs_file_path, sequence_file_path, subject_list_file_path, output_file_path):
        # generated, unique ID of the subject (consist of a name, a number and an optional group name
        self.subject_id = subject_id
        # path to the settings file of the current subject storing the state of the experiment
        self.all_settings_file_path = all_settings_file_path
        # path to the file containing the IDs for all subjects
        self.all_IDs_file_path = all_IDs_file_path
        # path to the file containing the sequence of the participant
        self.sequence_file_path = sequence_file_path
        # path to a text file containing a list of all subjects
        self.subject_list_file_path = subject_list_file_path
        # output text file for the measured data of the current subject
        self.output_file_path = output_file_path
        # we store all neccessary data in this list of lists to be able to generate the output at the end of all blocks
        self.output_data_buffer = []

    def load_person_settings(self, experiment):
        """Open settings file of the current subject and read the current state."""

        try:
            with shelve.open(self.all_settings_file_path, 'r') as this_person_settings:

                experiment.subject_age = this_person_settings['subject_age']
                experiment.subject_sex = this_person_settings['subject_sex']

                experiment.stim_sessionN = this_person_settings['stim_sessionN']
                experiment.stimblock = this_person_settings['stimblock']
                experiment.stimtrial = this_person_settings['stimtrial']

                experiment.stimlist = this_person_settings['stimlist']
                experiment.stimpr = this_person_settings['stimpr']
                experiment.last_N = this_person_settings['last_N']
                experiment.end_at = this_person_settings['end_at']
        except:
            experiment.subject_age = None
            experiment.subject_sex = None
            experiment.stim_sessionN = {}
            experiment.stimblock = {}
            experiment.stimtrial = {}
            experiment.stimlist = []
            experiment.stimpr = []
            experiment.last_N = 0
            experiment.end_at = {}

    def save_person_settings(self, experiment):
        """Write out the current state of the experiment run with current subject,
           so we can continue the experiment from that point where the subject finished it."""

        with shelve.open(self.all_settings_file_path, 'n') as this_person_settings:
            
            this_person_settings['subject_age'] = experiment.subject_age
            this_person_settings['subject_sex'] = experiment.subject_sex
     
            this_person_settings['stim_sessionN'] = experiment.stim_sessionN
            this_person_settings['stimblock'] = experiment.stimblock
            this_person_settings['stimtrial'] = experiment.stimtrial

            this_person_settings['stimlist'] = experiment.stimlist
            this_person_settings['stimpr'] = experiment.stimpr
            this_person_settings['last_N'] = experiment.last_N
            this_person_settings['end_at'] = experiment.end_at

    def update_all_subject_attributes_files(self, subject_sex, subject_age):
        """Add the new subject's attributes into the list of all subject data and save it into file.
           Also generate a text file with the list of all subjects participating in the experiment.
        """

        all_IDs = []
        with shelve.open(self.all_IDs_file_path) as all_subject_file:
            try:
                all_IDs = all_subject_file['ids']
            except:
                all_IDs = []

            if self.subject_id not in all_IDs:
                all_IDs.append(self.subject_id)
                all_subject_file['ids'] = all_IDs
                all_subject_file[self.subject_id] = [subject_sex, subject_age]

        with shelve.open(self.all_IDs_file_path, 'r') as all_subject_file:
            with codecs.open(self.subject_list_file_path, 'w', encoding='utf-8') as subject_list_file:
                subject_list_IO = StringIO()
                # write header
                subject_list_IO.write('subject_name\tsubject_id\tsubject_sex\tsubject_age\n')

                # write subject data
                for id in all_IDs:
                    id_segmented = id.replace('_', '\t', 2)
                    subject_list_IO.write(id_segmented)
                    subject_list_IO.write('\t')
                    subject_list_IO.write(all_subject_file[id][0])
                    subject_list_IO.write('\t')
                    subject_list_IO.write(all_subject_file[id][1])
                    subject_list_IO.write('\n')

                subject_list_file.write(subject_list_IO.getvalue())
                subject_list_IO.close()

    def append_to_output_file(self, string_to_append):
        """ Append a string to the end on the output text file."""

        if not os.path.isfile(self.output_file_path):
            with codecs.open(self.output_file_path, 'w', encoding='utf-8') as output_file:
                self.add_heading_to_output(output_file)
                output_file.write(string_to_append)
        else:
            with codecs.open(self.output_file_path, 'a+', encoding='utf-8') as output_file:
                output_file.write(string_to_append)

    def flush_data_to_output(self, experiment):
        """ Write out the ouptut date of the current trial into the output text file (reaction-time exp. type)."""
        
        output_buffer = StringIO()
        for data in self.output_data_buffer:
            N = data[0]

            output_data = [experiment.subject_name,
                           str(experiment.subject_number).zfill(2),
                           experiment.subject_sex,
                           experiment.subject_age,

                           experiment.stim_sessionN[N],
                           experiment.stimblock[N],
                           experiment.stimtrial[N],

                           data[1],
                           experiment.frame_rate,
                           experiment.frame_time,
                           experiment.frame_sd,
                           data[2],
                           data[3],

                           experiment.stimpr[N],
                           data[4],
                           data[5],
                           experiment.stimlist[N],
                           data[6]]
            output_buffer.write("\n")
            for data in output_data:
                if isinstance(data, numbers.Number):
                    data = str(data)
                    data = data.replace('.', ',')
                else:
                    data = str(data)
                output_buffer.write(data + '\t')

        self.append_to_output_file(output_buffer.getvalue())
        output_buffer.close()
        self.output_data_buffer.clear()

    def add_heading_to_output(self, output_file):
        """Add the first line to the ouput with the names of the different variables (reaction-time exp. type)."""
        
        heading_list = ['subject_name',
                        'subject_number',
                        'subject_sex',
                        'subject_age',

                        'session',
                        'block',
                        'trial',

                        'RSI_time',
                        'frame_rate',
                        'frame_time',
                        'frame_sd',
                        'time',
                        'date',

                        'trial_type',
                        'RT',
                        'error',
                        'stimulus',
                        'response',
                        'quit_log']

        for h in heading_list:
            output_file.write(h + '\t')
    
    
class Experiment: 
    """ Class for running the experiment. """

    def __init__(self, workdir_path):
        # working directory of the experiment, the script reads settings and writer output under this directory
        self.workdir_path = workdir_path

        # all experiment settings globally used for all subjects
        self.settings = None
        # instruction strings used to display messages during the experiment
        self.instructions = None
        # handler object for loadin and saving subject settings and output
        self.person_data = None

        # pressed button -> stimulus number maping (e.g. {'h': 1, 'j' : 2, 'k' : 3, 'l' : 4}
        self.pressed_dict = None
        # image to display
        self.image_dict = None
        
        self.fixation_cross = None
        
        self.shared_data_lock = threading.Lock()
        self.main_loop_lock = threading.Lock()

        # visual.Window object for displaying experiment
        self.mywindow = None
        self.mymonitor = None
        # avarage time of displaying one frame on the screen in ms (e.g. 15.93 for 50 Hz)
        self.frame_time = None
        # standard deviation of displaying one frame on the screen in ms (e.g. 0.02)
        self.frame_sd = None
        # measured frame rate in Hz (e.g. 59.45)
        self.frame_rate = None

        # serial number of the current subject
        self.subject_number = None
        # name of the current subject
        self.subject_name = None
        # sex of the subject (e.g. male, female, other)
        self.subject_sex = None
        # age of the subject (e.g. 23 (years))
        self.subject_age = None

        # serial number of the next line in the output file (e.g. 10)
        # self.stim_output_line = None
        # global trial number -> session number mapping (e.g. {1 : 1, 2 : 1, 3 : 2, 4 : 2} - two sessions with two trials in each)
        self.stim_sessionN = None
        # global trial number -> block number mapping (e.g. {1 : 1, 2 : 2, 3 : 2, 4 : 2} - two blocks with two trials in each)
        self.stimblock = None
        # global trial number -> trial number inside the block mapping (e.g. {1 : 1, 2 : 2, 3 : 1, 4 : 2} - two blocks with two trials in each)
        self.stimtrial = None
        # global trial number -> stimulus number mapping (e.g. {1 : 1, 2 : 2, 3 : 2, 4 : 4})
        self.stimlist = None
        # global trial number -> first trial of the next session mapping (e. g.{1 : 3, 2 : 3, 3 : 5, 4 : 5} - two sessions with two trials in each)
        self.end_at = None
        # global trial number -> pattern or random stimulus mapping (e. g.{1 : 'pattern', 2 : 'random', 3 : 'pattern', 4 : 'random'} - two sessions with two trials in each)
        self.stimpr = None
        # number of the last trial (it is 0 in the beggining and it is always equal with the last displayed stimulus's serial number
        self.last_N = None
        # this variable has a meaning during presentation, showing the phase of displaying the current stimulus
        # possible values: "before_stimulus", "stimulus_on_screen", "after_reaction"
        self.trial_phase = None
        # this variable has a meaning during presentation, last measured RSI
        self.last_RSI = None

    def all_settings_def(self):
        try:
            self.settings.read_from_file()
        except:
            self.settings.show_basic_settings_dialog()
            self.settings.show_computer_and_display_settings_dialog()
            self.settings.show_key_and_feedback_settings_dialog()
            self.settings.write_to_file()
            self.settings.write_out_reminder()
    
    def show_subject_identification_dialog(self):
        """Ask the user to specify the subject's attributes (name, subject number, group)."""

        warningtext = ''
        itsOK = False
        while not itsOK:
            settings_dialog = gui.Dlg(title='Settings')
            settings_dialog.addText(warningtext, color='Red')
            settings_dialog.addField('Name', "John Doe")
            settings_dialog.addField('Participant Number', str(1).zfill(2))

            returned_data = settings_dialog.show()
            if settings_dialog.OK:
                name = returned_data[0]
                name = normalize_string(name, '-')
                name = name.replace("_", "-")
                self.subject_name = name

                subject_number = returned_data[1]
                try:
                    subject_number = int(subject_number)
                    if subject_number >= 0:
                        itsOK = True
                        self.subject_number = subject_number
                    else:
                        warningtext = 'Enter a positive participant number!'
                        continue

                except:
                    warningtext = 'Enter a positive participant number!'
                    continue
            else:
                core.quit()

    def show_subject_continuation_dialog(self):
        """Dialog shown after restart of the experiment for a subject.
           Displays the state of the experiment for the given subject."""

        if self.last_N + 1 <= self.settings.maxtrial_traintest():
            expstart11 = gui.Dlg(title='Starting task...')
            expstart11.addText("Already have participant's data")
            expstart11.addText('Continue from here...')
            expstart11.addText('Session: ' + str(self.stim_sessionN[self.last_N + 1]))
            expstart11.addText('Block: ' + str(self.stimblock[self.last_N + 1]))
            expstart11.show()
            if not expstart11.OK:
                core.quit()
        else:
            expstart11 = gui.Dlg(title='Continue from here...')
            expstart11.addText("Already have participant's data")
            expstart11.addText('Participant completed the task.')
            expstart11.show()
            core.quit()

    def show_subject_attributes_dialog(self):
        """Select pattern sequences for the different sessions for the current subject."""

        settings_dialog = gui.Dlg(title='Settings')
        settings_dialog.addField('Sex', choices=["male", "female"])
        settings_dialog.addField('Age', "18")
        
        returned_data = settings_dialog.show()
        if settings_dialog.OK:

            subject_sex = returned_data[0]
            subject_age = returned_data[1]
            
            if subject_sex == 'male':
                self.subject_sex = 'male'
            elif subject_sex == 'female':
                self.subject_sex = 'female'
            else:
                self.subject_sex = 'other'

            try:
                subject_age = int(subject_age)
                self.subject_age = str(subject_age)
            except:
                core.quit()
        else:
            core.quit()

    def create_sequence(self):
        """Generates csv file with list of stimuli for current session."""
        
        keys = [1, 2, 3, 4]
        trials = np.arange(self.settings.maxtrial_traintest())
        tests = self.settings.trials_in_block
        random = tests/2
        data = pd.DataFrame({'trials': trials,
                             'trial_keys': np.zeros(len(trials), dtype=int),
                             'trial_type': ['to_define']*len(trials)})

        np.random.shuffle(keys)
        
        if self.settings.current_session == 1:
            for trial in trials:
                if trial in np.arange((self.settings.trials_in_tBlock), (tests + 1), self.settings.trials_in_block):
                    data.trial_keys.at[trial] = np.random.choice(keys)
                    data.trial_type.at[trial] = 'no transition'
                elif trial in np.arange(0, (self.settings.trials_in_tBlock)):
                    data.trial_keys.at[trial] = np.random.choice(keys)
                    data.trial_type.at[trial] = 'training'
                elif trial in np.arange((self.settings.trials_in_tBlock), (self.settings.trials_in_tBlock + random)):
                    data.trial_keys.at[trial] = np.random.choice(keys)
                    data.trial_type.at[trial] = 'random'                
                else:
                    if data.trial_keys[trial-1] == keys[0]:
                        data.trial_keys.at[trial] = keys[1]
                        data.trial_type.at[trial] = 'deterministic'
                    elif data.trial_keys[trial-1] == keys[1]:
                        data.trial_keys.at[trial] = keys[np.random.choice([0, 2, 3])]
                        data.trial_type.at[trial] = 'pseudo-random'
                    elif data.trial_keys[trial-1] == keys[2]:
                        if np.random.random() < 2/3.:
                            data.trial_keys.at[trial] = keys[3]
                            data.trial_type.at[trial] = 'high_prob'
                        else:
                            data.trial_keys.at[trial] = keys[0]
                            data.trial_type.at[trial] = 'low_prob'
                    elif data.trial_keys[trial-1] == keys[3]:
                        if np.random.random() < 2/3:
                            data.trial_keys.at[trial] = keys[2]
                            data.trial_type.at[trial] = 'high_prob'
                        else:
                            data.trial_keys.at[trial] = keys[0]
                            data.trial_type.at[trial] = 'low_prob'
        else:
            for trial in trials:
                if trial in np.arange((self.settings.trials_in_tBlock + 1), (tests + 1), self.settings.trials_in_block):
                    data.trial_keys.at[trial] = np.random.choice(keys)
                    data.trial_type.at[trial] = 'no transition'
                elif trial in np.arange(0, (self.settings.trials_in_tBlock + 1)):
                    data.trial_keys.at[trial] = np.random.choice(keys)
                    data.trial_type.at[trial] = 'training'
                elif trial in np.arange((random + 1), (tests + 1)):
                    data.trial_keys.at[trial] = np.random.choice(keys)
                    data.trial_type.at[trial] = 'random'
                else:
                    if data.trial_keys[trial-1] == keys[0]:
                        data.trial_keys.at[trial] = keys[1]
                        data.trial_type.at[trial] = 'deterministic'
                    elif data.trial_keys[trial-1] == keys[1]:
                        data.trial_keys.at[trial] = keys[np.random.choice([0, 2, 3])]
                        data.trial_type.at[trial] = 'pseudo-random'
                    elif data.trial_keys[trial-1] == keys[2]:
                        if np.random.random() < 2/3.:
                            data.trial_keys.at[trial] = keys[3]
                            data.trial_type.at[trial] = 'high_prob'
                        else:
                            data.trial_keys.at[trial] = keys[0]
                            data.trial_type.at[trial] = 'low_prob'
                    elif data.trial_keys[trial-1] == keys[3]:
                        if np.random.random() < 2/3:
                            data.trial_keys.at[trial] = keys[2]
                            data.trial_type.at[trial] = 'high_prob'
                        else:
                            data.trial_keys.at[trial] = keys[0]
                            data.trial_type.at[trial] = 'low_prob'
 
        data.to_csv(f'{self.settings.sequence_file_path}/{str(self.subject_number).zfill(2)}_seq_{self.settings.current_session}.csv')        
            
    def open_sequence(self):
        """Returns lists of stimuli sequence and type for current session."""
        
        try:
            data = pd.read_csv(f'{self.settings.sequence_file_path}/{str(self.subject_number).zfill(2)}_seq_{self.settings.current_session}.csv', 
                           sep=',', header=0, encoding='utf8')
        except:
            self.create_sequence()
            data = pd.read_csv(f'{self.settings.sequence_file_path}/{str(self.subject_number).zfill(2)}_seq_{self.settings.current_session}.csv', 
                sep=',', header=0, encoding='utf8')

        seq = list(data['trial_keys'])
        stim_type = list(data['trial_type'])
        
        return seq, stim_type
    

    def calculate_stim_properties(self):
        """Calculate all variables used during the trials before the presentation starts."""
        
        (self.stimlist, self.stimpr) = self.open_sequence()

        all_trial_Nr = 0
        block_num = 0
        sessionsstarts = self.settings.get_session_starts()
        
        for trial_num in range(1, self.settings.maxtrial_traintest() + 1):
            for session_num in range(1, len(sessionsstarts)):
                if trial_num >= sessionsstarts[session_num - 1] and trial_num < sessionsstarts[session_num]:
                    self.stim_sessionN[trial_num] = session_num
                    self.end_at[trial_num] = sessionsstarts[session_num]         


        for block in range(1, self.settings.blocks_in_session + 1):

            block_num += 1
            current_trial_num = 0
    
            # training
            
            for train in range(1, self.settings.trials_in_tBlock + 1):
                current_trial_num += 1
                all_trial_Nr += 1      

                self.stimtrial[all_trial_Nr] = current_trial_num
                self.stimblock[all_trial_Nr] = block_num
                                
            # testing
            
            for test in range(self.settings.trials_in_tBlock + 1, self.settings.maxtrial_traintest() + 1):
                current_trial_num += 1
                all_trial_Nr += 1
                                    
                self.stimtrial[all_trial_Nr] = current_trial_num
                self.stimblock[all_trial_Nr] = block_num
                
    def participant_id(self):
        """Find out the current subject and read subject settings / progress if he/she already has any data."""

        self.show_subject_identification_dialog()

        # unique subject ID
        subject_id = self.subject_name + '_' + str(self.subject_number).zfill(2)

        # init subject data handler with the right file paths
        all_settings_file_path = os.path.join(self.workdir_path, "settings", subject_id)
        all_IDs_file_path = os.path.join(self.workdir_path, "settings", "participant_settings")
        sequence_file_path = os.path.join(self.workdir_path, "sequences", 
                                          str(self.subject_number) + '_seq' + str(self.settings.current_session) + '.csv')
        subject_list_file_path = os.path.join(self.workdir_path, "settings",
                                            "participants_in_experiment.txt")
        # output_file_path = os.path.join(self.workdir_path, "logs", subject_id + '_log.txt')
        output_file_path = os.path.join(self.workdir_path, "logs", subject_id + '_log' + str(self.settings.current_session)+ '.txt')
        self.person_data = PersonDataHandler(subject_id, all_settings_file_path,
                                            all_IDs_file_path, sequence_file_path, subject_list_file_path,
                                            output_file_path)

        # try to load settings and progress for the given subject ID
        self.person_data.load_person_settings(self)

        if self.last_N > 0:
            # the current subject already started the experiment
            self.show_subject_continuation_dialog()
            self.open_sequence()
        # we have a new subject
        else:
            # ask about the pattern codes used in the different sessions
            self.show_subject_attributes_dialog()
            # update participant attribute filesf
            self.person_data.update_all_subject_attributes_files(self.subject_sex, self.subject_age)
            # create sequence for current session
            self.open_sequence()
            # calculate stimulus properties for the experiment
            self.calculate_stim_properties()
            # save data of the new subject
            self.person_data.save_person_settings(self)

    def monitor_settings(self):
        """Specify monitor settings."""

        # use default screen resolution
        screen = pyglet.canvas.get_display().get_default_screen()
        self.mymonitor = monitors.Monitor('myMon')
        self.mymonitor.setSizePix([screen.width, screen.height])
        # need to set monitor width in cm to be able to use cm unit for stimulus
        self.mymonitor.setWidth(self.settings.monitor_width)
        self.mymonitor.saveMon()

    def print_to_screen(self, mytext):
        """Display any string on the screen."""

        xtext = visual.TextStim(self.mywindow, text=mytext,
                                units="cm", height=0.8, wrapWidth=20, 
                                color="black")
        xtext.draw()
        self.mywindow.flip()


    def frame_check(self):
        """Measure the frame rate, using different measurements."""

        self.print_to_screen(
            "Preparation...")
        core.wait(2)

        ms_per_frame = self.mywindow.getMsPerFrame(nFrames=120)
        self.frame_time = ms_per_frame[0]
        self.frame_sd = ms_per_frame[1]
        self.frame_rate = self.mywindow.getActualFrameRate()

    
    def show_feedback(self, N, responses_in_block, accs_in_block, RT_all_list):
        """ Display feedback in the end of the blocks, showing some data about speed and accuracy."""

        acc_for_the_whole = 100 * float(responses_in_block - sum(accs_in_block)) / responses_in_block
        acc_for_the_whole_str = str(acc_for_the_whole)[0:5].replace('.', ',')

        rt_mean = float(sum(RT_all_list)) / len(RT_all_list)
        rt_mean_str = str(rt_mean)[:5].replace('.', ',')

        whatnow = self.instructions.feedback_RT_acc(
            rt_mean, rt_mean_str, acc_for_the_whole, acc_for_the_whole_str, self.mywindow, self.settings)

    
    def wait_for_response(self, expected_response, response_clock):
        press = event.waitKeys(keyList=self.settings.get_key_list(),
                               timeStamped=response_clock)
        if press[0][0] == 'q':
            return (-1, press[0][1])
        return (self.pressed_dict[press[0][0]], press[0][1])
    
    def quit_presentation(self):
        self.print_to_screen("Exiting...\nSaving data...")
        self.person_data.append_to_output_file('userquit')
        core.wait(3)
        core.quit()
    
    def resting_period(self, fixation_cross, experiment):
        """Resting time with eyes closed."""
                    
        self.print_to_screen("Fermez vos yeux puis appuyez sur un bouton.")
        tempkey = event.waitKeys(keyList=experiment.get_key_list())
        
        s = sound.Sound('A', secs=.5, stereo=True, hamming=True, volume=1.0)
                
        if experiment.key_quit in tempkey:
            self.quit_presentation()
        else:
            self.mywindow.flip()
            rest_time = core.CountdownTimer(self.settings.rest_time)
            while rest_time.getTime() > 1:
                fixation_cross.draw()
                self.mywindow.flip()
            s.play()
            while rest_time.getTime() > 0:
                fixation_cross.draw()
                self.mywindow.flip()
                
    def presentation(self):
        """The real experiment happens here. This method displays the stimulus window and records the RTs."""
        
        # fixation cross
        fixation_cross = visual.TextStim(win=self.mywindow, text="+", 
                                              units="cm", height=1,
                                              color='black', opacity=.7,
                                              pos=(0,0))
        
        # fixation_cross = visual.ShapeStim(win=self.mywindow, name='polygon', vertices='cross',
        #                                   size=(1, 1), pos=(0, 0), anchor='center',
        #                                   lineWidth=1.0, colorSpace='rgb',  lineColor='black', fillColor='black',
        #                                   opacity=1, depth=0.0, interpolate=True)
    
                
        # Photodiode configuration
        screen = pyglet.canvas.get_display().get_default_screen()
        pixel = visual.Rect(win=self.mywindow, units='pix', 
                            pos=(-screen.height, screen.height/2),
                            size=(screen.width*2/5, 200),
                            fillColor='black', lineColor='black')
        pixel.setAutoDraw(False) # set to True/False to activate/deactivate the photodiode
        del screen
        
        # negative feedback during training block
        red = visual.Circle(win=self.mywindow, units='pix', radius=65,
                            lineColor='red', fillColor='red',
                            opacity=.50)
        
        
        stim_RSI = 0.0
        N = self.last_N + 1
    
        responses_in_block = 0
        accs_in_block = []
                
        num_of_random = 0
        num_of_high = 0
        num_of_low = 0
                
        RT_random_list = []
        RT_high_list = []
        RT_low_list = []
        RT_all_list = []
        
        err_random = 0
        err_high = 0
        err_low = 0
        err_all = 0
                
        RSI = core.StaticPeriod(screenHz=self.frame_rate)
        RSI_clock = core.Clock()
        trial_clock = core.Clock()
        
        first_trial_in_block = True
        
        self.trial_phase = "before_stimulus"
        self.last_RSI = -1
        
        # show instructions or continuation message
        if N in self.settings.get_session_starts():
            self.instructions.show_instructions(self)
        else:
            self.instructions.show_unexp_quit(self)
        
        RSI.start(self.settings.RSI_time)
        while True:
            
            fixation_cross.draw()
            stim = visual.ImageStim(win=self.mywindow, image=self.image_dict[self.stimlist[0]], 
                                    pos=(0,0), units='pix', size=(128, 128), opacity=1)
            self.mywindow.flip()

            with self.shared_data_lock:
                self.last_N = N - 1
                self.trial_phase = "before stimulus"
                self.last_RSI = -1
            
            # wait before the next stimulus to have the set RSI
            RSI.complete()
            
            cycle = 0
            
            while True: 
                cycle += 1
                
                stim = visual.ImageStim(win=self.mywindow, image=self.image_dict[self.stimlist[N]], 
                                        pos=(0,0), units='pix', size=(128, 128), opacity=1)
                stim.draw()
                fixation_cross.draw()
                self.mywindow.flip()
                
                if cycle == 1:
                    if first_trial_in_block:
                        stim_RSI = 0.0
                    else:
                        stim_RSI = RSI_clock.getTime()
                
                with self.shared_data_lock:
                    self.trial_phase = "stimulus_on_screen"
                    self.last_RSI = stim_RSI
                
                if cycle == 1:
                    trial_clock.reset()
                (response, time_stamp) = self.wait_for_response(self.stimlist[N], trial_clock)
                
                with self.shared_data_lock:
                    self.trial_phase = "after_reaction"
                
                now = datetime.now()                
                stim_RT_time = now.strftime('%H:%M:%S.%f')
                stim_RT_date = now.strftime('%d/%m/%Y')
                stimRT = time_stamp
                
                responses_in_block += 1
                
                # quit during the experiment
                if response == -1:
                    if N >= 1:
                        with self.shared_data_lock:
                            self.last_N = N - 1
                    self.quit_presentation()
                
                # correct response
                elif response == self.stimlist[N]:
                    # start of the RSI timer and offset of the stimulus
                    stim.setOpacity(0)
                    stim.draw()
                    self.mywindow.flip()
                    RSI_clock.reset()
                    RSI.start(self.settings.RSI_time)
                    stimACC = 0
                    accs_in_block.append(0)
                    if self.stimpr[N] == 'random':
                        num_of_random += 1
                        RT_random_list.append(stimRT)
                    elif self.stimpr[N] == 'high_prob':
                        num_of_high += 1
                        RT_high_list.append(stimRT)
                    elif self.stimpr[N] == 'low_prob':
                        num_of_low += 1
                        RT_low_list.append(stimRT)
                    RT_all_list.append(stimRT)             
                
                # wrong response --> let's wait for the next response
                else:
                    stimACC = 1
                    accs_in_block.append(1)
                    if self.stimpr[N] == 'training':
                        timer = core.CountdownTimer(.2)
                        while timer.getTime() > 0:
                            fixation_cross.draw()
                            red.draw()
                            self.mywindow.flip()
                    elif self.stimpr[N] == 'random':
                        num_of_random += 1
                        RT_random_list.append(stimRT)
                        err_random += 1
                    elif self.stimpr[N] == 'high_prob':
                        num_of_high += 1
                        RT_high_list.append(stimRT)
                        err_high += 1
                    elif self.stimpr[N] == 'low_prob':
                        num_of_low += 1
                        RT_low_list.append(stimRT)
                        err_low += 1
                    RT_all_list.append(stimRT)
                    err_all += 1
                
                # save data of the last trial
                self.person_data.output_data_buffer.append([N, stim_RSI, stim_RT_time, stim_RT_date,
                                                                stimRT, stimACC, response])

                if stimACC == 0:
                    N += 1
                    first_trial_in_block = False
                    break
            
            # resting period only
            if N in self.settings.get_block_starts() and N not in self.settings.get_fb_block():

                with self.shared_data_lock:
                    self.last_N = N - 1
                    self.trial_phase = "before stimulus"
                    self.last_RSI = - 1
                                
                self.resting_period(fixation_cross, self.settings)
                self.person_data.flush_data_to_output(self)
                self.person_data.save_person_settings(self)

                first_trial_in_block = True

            # resting period and feedback   
            if N in self.settings.get_fb_block()[1:]:
                                                
                with self.shared_data_lock:
                    self.last_N = N - 1
                    self.trial_phase = "before stimulus"
                    self.last_RSI = - 1
                                
                self.resting_period(fixation_cross, self.settings)
                self.person_data.flush_data_to_output(self)
                self.person_data.save_person_settings(self)

                timer = core.CountdownTimer(self.settings.rest_time)
                while timer.getTime() > 0:
                    self.show_feedback(N, responses_in_block,accs_in_block, RT_all_list)
                
                responses_in_block = 0
                RT_all_list = []
                accs_in_block = []
                first_trial_in_block = True
            
            # end of training
            if N == (self.settings.trials_in_tBlock):
                # self.instructions.show_training_end(self)
                self.print_to_screen("Fin de l'entraînement. \n\n Appuyez sur une touche pour lancer la vraie tache !")
                press = event.waitKeys(keyList=self.settings.get_key_list())
                if self.settings.key_quit in press:
                    core.quit()
            
            # end of the sessions (one run of the experiment script stops at the end of the current session)
            if N == self.end_at[N - 1]:
            # if N == (len(self.stimlist) - 1):    
                self.print_to_screen("Fin de la tâche. Merci d'avoir participé.")
                core.wait(5)
                break

    def run(self, full_screen=False, mouse_visible=True, window_gammaErrorPolicy='raise', 
            parallel_port=False,
            eyetrack=False):
        
        if parallel_port:
            addressPortParallel = '0x3FE8'
            port = parallel.ParallelPort(address=addressPortParallel)

            # Start the MEG recordings
            port.setData(0)
            time.sleep(0.1)
            port.setData(252)
            
            # Serial port
            # to read button presses from the button box
            port_s = serial_port()
    
        # ensure all required folders are created, if not creates them
        ensure_dir(os.path.join(self.workdir_path, "logs"))
        ensure_dir(os.path.join(self.workdir_path, "settings"))
        ensure_dir(os.path.join(self.workdir_path, "sequences"))
        
        # load experiment settings if exist or ask the user to specify them
        all_settings_file_path = os.path.join(self.workdir_path, "settings", "settings")
        reminder_file_path = os.path.join(self.workdir_path, "settings", "settings_reminder.txt")
        sequence_file_path = os.path.join(self.workdir_path, "sequences")
        self.settings = ExperimentSettings(all_settings_file_path, reminder_file_path, sequence_file_path)
        self.all_settings_def()

        self.pressed_dict = {self.settings.key1: 1, self.settings.key2: 2,
                             self.settings.key3: 3, self.settings.key4: 4}
        
        # create sorted list of stimuli images
        images = []
        files_list = os.listdir(op.join(self.workdir_path, 'stimuli'))
        for img in files_list:
            if '.tiff' in img:
                images.append(img)
        images.sort()        
        
        # create dictionary matching images and corresponding stimulus number
        self.image_dict = {1:op.join(self.workdir_path, 'stimuli', images[0]),
                           2:op.join(self.workdir_path, 'stimuli', images[1]),
                           3:op.join(self.workdir_path, 'stimuli', images[2]),
                           4:op.join(self.workdir_path, 'stimuli', images[3])}

        # read instruction strings
        inst_feedback_path = os.path.join(self.workdir_path, "inst_and_feedback.txt")
        self.instructions = InstructionHelper(inst_feedback_path)
        self.instructions.read_insts_from_file()
        self.instructions.validate_instructions(self.settings)

        # find out the current subject
        self.participant_id()

        # init window
        self.monitor_settings()
        with visual.Window(size=self.mymonitor.getSizePix(), color='Ivory', fullscr=False, 
                           monitor=self.mymonitor, units="pix", gammaErrorPolicy=window_gammaErrorPolicy) as self.mywindow:
            
            self.mywindow.mouseVisible = mouse_visible

            # check frame rate
            self.frame_check()

            # show experiment screen
            self.presentation()

            # save user data
            self.person_data.save_person_settings(self)
            self.person_data.append_to_output_file('sessionend_planned_quit')

            # show ending screen
            self.instructions.show_ending(self)
            
            if parallel_port:
                # Stop MEG recordings
                time.sleep(1)
                port.setData(253)
                time.sleep(1)
                port.setData(0)


if __name__ == "__main__":
    thispath = os.path.split(os.path.abspath(__file__))[0]
    experiment = Experiment(thispath)
    experiment.run()