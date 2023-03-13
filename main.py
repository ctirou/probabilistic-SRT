from psychopy import visual, core, event, gui, monitors, sound, parallel, prefs
import psychtoolbox as ptb
# import pygame
# import pygame_menu
# from pygame_menu import widgets
from serial import Serial
import time
import shelve
import codecs
import os
import pyglet
import numbers
from datetime import datetime
from io import StringIO
import threading
import os.path as op
import pandas as pd
import numpy as np
from math import atan2, degrees, fabs

debug_mode = False
meg_session = False
eyetracking = False
tutorial = True
resting_state = False

if debug_mode:
    mouse_visible = True
    full_screen = False
    screen_width = 1920
    screen_height = 1080
    resting_time = 1
    
else:
    mouse_visible = False
    full_screen = False
    screen_width = 1920
    screen_height = 1080

if eyetracking:
    import pylink
    from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy
    import sys
    from string import ascii_letters, digits

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

if meg_session:
    try:
        addressPortParallel = '0x3FE8'
    except:
        addressPortParallel = '0x3FF8'
    print(addressPortParallel)
    #receive responses
    port_s = serial_port()
    # send triggers
    port = parallel.ParallelPort(address=addressPortParallel)

try:
    root = op.dirname(op.abspath(__file__))
except NameError:
    import sys
    root = op.dirname(op.abspath(sys.argv[0]))

def ensure_dir(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    
class ExperimentSettings:
    """
        This class handles all operation related to experiment settings.
        These settings apply to all subjects in the specific experiment.
    """

    def __init__(self, settings_file_path, reminder_file_path, sequence_file_path):

        self.numsessions = 2 # number of sessions
        self.current_session = None # current session

        self.blocks_in_session = None
        self.trials_in_pretrain = None
        self.trials_in_tBlock = None
        self.trials_in_block = None
        
        self.computer_name = None
        self.monitor_width = None
        self.monitor_height = None
        self.monitor_distance = None

        self.RSI_time = None # response-to-next-stimulus in milliseconds
        self.rest_time = None # resting period duration in seconds
        self.rs_time = None # resting state time in seconds

        self.key1 = None
        self.key2 = None
        self.key3 = None
        self.key4 = None
        self.key5 = None
        self.key_resume = 'c'
        self.key_quit = None

        self.whether_warning = None
        self.speed_warning = None
        self.acc_warning = None

        self.sessionstarts = None
        self.blockstarts = None
        self.fb_block = None
        
        self.el_tracker = None
        # AOI (area of interest) is a square with the same origin as the stimuli, this size means the size of this square's side
        self.AOI_size = None
        # count of samples used to identify fixation
        self.fixation_threshold = None
        # dispersion threshold in cm
        self.dispersion_threshold = None

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
                self.trials_in_pretrain = settings_file['trials_in_pretrain']
                self.trials_in_tBlock = settings_file['trials_in_tBlock']
                self.trials_in_block = settings_file['trials_in_block']
                
                self.computer_name = settings_file['computer_name']
                self.monitor_width = settings_file['monitor_width']
                self.monitor_height = settings_file['monitor_height']
                self.monitor_distance = settings_file['monitor_distance']

                self.RSI_time = settings_file['RSI_time']
                self.rest_time = settings_file['rest_time']
                self.rs_time = settings_file['rs_time']

                self.key1 = settings_file['key1']
                self.key2 = settings_file['key2']
                self.key3 = settings_file['key3']
                self.key4 = settings_file['key4']
                self.key5 = settings_file['key5']
                self.key_resume = settings_file['key_resume']
                self.key_quit = settings_file['key_quit']

                self.whether_warning = settings_file['whether_warning']
                self.speed_warning = settings_file['speed_warning']
                self.acc_warning = settings_file['acc_warning']
                
                if eyetracking:
                    self.AOI_size = settings_file['AOI_size']
                    self.fixation_threshold = settings_file['fixation_threshold']
                    self.dispersion_threshold = settings_file['dispersion_threshold']

        except Exception as exception:
            self.__init__(self.settings_file_path, self.reminder_file_path, self.sequence_file_path)
            raise exception

    def write_to_file(self):
        """Create a new settings file and write all settings into it."""

        with shelve.open(self.settings_file_path, 'n') as settings_file:
            settings_file['numsessions'] = self.numsessions

            settings_file['blocks_in_session'] = self.blocks_in_session
            settings_file['trials_in_pretrain'] = self.trials_in_pretrain
            settings_file['trials_in_tBlock'] = self.trials_in_tBlock
            settings_file['trial_in_block'] = self.trials_in_block
            
            settings_file['computer_name'] = self.computer_name
            settings_file['monitor_width'] = self.monitor_width
            settings_file['monitor_height'] = self.monitor_height
            settings_file['monitor_distance'] = self.monitor_distance

            settings_file['RSI_time'] = self.RSI_time
            settings_file['rest_time'] = self.rest_time
            settings_file['rs_time'] = self.rs_time

            settings_file['key1'] = self.key1
            settings_file['key2'] = self.key2
            settings_file['key3'] = self.key3
            settings_file['key4'] = self.key4
            settings_file['key5'] = self.key5
            settings_file['key_resume'] = self.key_resume
            settings_file['key_quit'] = self.key_quit

            settings_file['whether_warning'] = self.whether_warning
            settings_file['speed_warning'] = self.speed_warning
            settings_file['acc_warning'] = self.acc_warning
            
            if eyetracking:
                settings_file['AOI_size'] = self.AOI_size
                settings_file['fixation_threshold'] = self.fixation_threshold
                settings_file['dispersion_threshold'] = self.dispersion_threshold


    def write_out_reminder(self):
        """Write out a short summary of the settings into a text file."""

        with codecs.open(self.reminder_file_path, 'w', encoding='utf-8') as reminder_file:
            reminder = str('Settings\n' +
                           '\n' +
                           'Computer Name: ' + '\t' + self.computer_name + '\n' +
                           'Monitor Width: ' + '\t' + str(self.monitor_width).replace('.', ',') + '\n' +
                           'Monitor Height: ' + '\t' + str(self.monitor_height).replace('.', ',') + '\n' +
                           'Distance to monitor: ' + '\t' + str(self.monitor_distance).replace('.', ',') + '\n')

            reminder += str('Response keys: ' + '\t' + self.key1 + ', ' + self.key2 + ', ' + self.key3 + ', ' + self.key4 + ',' + self.key5 + '.' + '\n' +
                            'Resume key: ' + '\t' + self.key_resume + '\n' +
                            'Quit key: ' + '\t' + self.key_quit + '\n' +
                            'Warning (speed, accuracy): ' + '\t' + str(self.whether_warning) + '\n' +
                            'Speed warning at:' + '\t' + str(self.speed_warning) + '\n' +
                            'Acc warning at:' + '\t' + str(self.acc_warning) + '\n')

            reminder += str('Sessions:' + '\t' + str(self.numsessions) + '\n' +
                            'Blocks per session: ' + '\t' + str(self.blocks_in_session) + '\n' +
                            'Training Trials\\Block:' + '\t' + str(self.trials_in_tBlock) + '\n' +
                            'Trials\\Block:' + '\t' + str(self.trials_in_block) + '\n' +
                            'RSI:' + '\t' + str(self.RSI_time).replace('.', ',') + '\n'
                            'Resting time: ' + '\t' + str(self.rest_time).replace('.', ',') + '\n' +
                            'Resting state time:' + '\t' + str(self.rs_time).replace('.', ',') + '\n')
            
            if eyetracking:
                reminder += str('AOI size:' + '\t' + str(self.AOI_size).replace('.', ',') + '\n' +
                                'Fixation threshold:' + '\t' + str(self.fixation_threshold) + '\n' +
                                'Dispersion threshold:' + '\t' + str(self.dispersion_threshold).replace('.', ',') + '\n')

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

    def get_maxtrial(self, what):
        
        """Get total number of trials:
                'all' : in all sessions, tutorial and training included
                'preTrainTest': per session, tutorial and training included
                'trainTest': per session, training included, tutorial excluded
                'test': per session, tutorial and training exluded
        """
        
        if what == 'all+tuto':
            return (self.trials_in_block * self.blocks_in_session + self.trials_in_pretrain + self.trials_in_tBlock) * self.numsessions
        elif what == 'all':
            return (self.trials_in_block * self.blocks_in_session + self.trials_in_tBlock) * self.numsessions
        elif what == 'preTrainTest':
            return (self.trials_in_block * self.blocks_in_session + self.trials_in_pretrain + self.trials_in_tBlock)
        elif what == 'trainTest':
            return (self.trials_in_block * self.blocks_in_session + self.trials_in_tBlock)
        elif what == 'test':
            return (self.trials_in_block * self.blocks_in_session)

    def get_block_starts(self):
        """Return with a list of numbers indicating the first trials of the different blocks."""

        if self.blockstarts == None:
            self.blockstarts = [1]
            for i in range(1, self.blocks_in_session + 2):
                self.blockstarts.append(i * self.trials_in_block + 1)
                # self.blockstarts.append(i * self.trials_in_block)

        return self.blockstarts

    def get_fb_block(self):
        """Returns with a list of numbers indicating when the feedback must be shown."""

        if self.fb_block == None:
            self.fb_block = []
            for i in range(self.trials_in_tBlock, (self.get_maxtrial('trainTest') + 1), (self.trials_in_block * 4)):
                self.fb_block.append(i + 1)

        return self.fb_block

    def get_session_starts(self):
        """Return with a list of numbers indicating the first trials of the different sessions."""

        if self.sessionstarts == None:
            self.sessionstarts = [1]
            epochs_cumulative = []
            e_temp = 0

            for e in range(self.numsessions):
                e_temp += e
                epochs_cumulative.append(e_temp)

            for e in epochs_cumulative:
                if e != 0:
                    self.sessionstarts.append(e * self.blocks_in_session * self.trials_in_block + self.trials_in_tBlock + 1)

        return self.sessionstarts

    def get_key_list(self):
        return (self.key1, self.key2, self.key3, self.key4, self.key5, self.key_quit)

    def show_basic_settings_dialog(self):
        """ Ask the user to specify the number of groups and the number of sessions."""

        settings_dialog = gui.Dlg(title='Experiment design')
        settings_dialog.addText('No settings saved for this experiment yet...')
        settings_dialog.addField('Current session:', choices=['1st', '2nd'])
        settings_dialog.addField('Blocks per session', 120)
        settings_dialog.addField('Trials in pre-training', 30)
        settings_dialog.addField('Trials in training block', 40)
        settings_dialog.addField('Trials per testing block', 20)
        returned_data = settings_dialog.show()
        if settings_dialog.OK:
            if returned_data[0] == '1st':
                self.current_session = 1
            else:
                self.current_session = 2
            if debug_mode:
                self.blocks_in_session = 6
                self.trials_in_pretrain = 1
                self.trials_in_tBlock = 1
                self.trials_in_block = 1
            else:
                self.blocks_in_session = returned_data[1]
                self.trials_in_pretrain = returned_data[2]
                self.trials_in_tBlock = returned_data[3]
                self.trials_in_block = returned_data[4]
        else:
            core.quit()

    def show_computer_and_display_settings_dialog(self):
        """Ask the user specific information about the computer and also change display settings."""

        settings_dialog = gui.Dlg(title='Settings')
        settings_dialog.addText('On the monitor...')
        settings_dialog.addField('Computer name', 'CERMEP_bat_452')
        settings_dialog.addField('Monitor Width (cm)', 34.2)
        settings_dialog.addField('Monitor Height (cm)', 28.62)
        settings_dialog.addField('Distance to monitor (cm)', 80)
        settings_dialog.addText('On timings...')
        settings_dialog.addField('RSI (ms)', 125)
        settings_dialog.addField('Resting time (s)', 5)
        settings_dialog.addField('Resting state time (s)', 240)

        returned_data = settings_dialog.show()

        if settings_dialog.OK:
            self.computer_name = returned_data[0]
            self.monitor_width = returned_data[1]
            self.monitor_height = returned_data[2]
            self.monitor_distance = returned_data[3]
            self.RSI_time = float(returned_data[4]) / 1000
            self.rs_time = float(returned_data[6])
            if debug_mode:
                self.rest_time = float(resting_time)
            else:
                self.rest_time = float(returned_data[5])
                
        else:
            core.quit()


    def show_key_and_feedback_settings_dialog(self):
        """Ask the user to specify the keys used during the experiement and also set options related to the displayed feedback."""

        settings_dialog = gui.Dlg(title='Settings')
        settings_dialog.addText('Answer keys')
        settings_dialog.addField('1:', 'y')
        settings_dialog.addField('2:', 'u')
        settings_dialog.addField('3:', 'i')
        settings_dialog.addField('4:', 'o')
        settings_dialog.addField('5:', 'space')
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
            self.key5 = returned_data[4]
            self.key_quit = returned_data[5]
            self.whether_warning = returned_data[6]
            self.speed_warning = returned_data[7]
            self.acc_warning = returned_data[8]
        else:
            core.quit()                


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
                                    units='cm', height=0.7, wrapWidth=20, color='black')
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

    # def show_training_end(self, experiment):
    #     self.__show_message(self.training_end, experiment)

    def show_unexp_quit(self, experiment):
        self.__show_message(self.unexp_quit, experiment)

    # def show_ending(self, experiment):
    #     self.__show_message(self.ending, experiment)


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
                
                experiment.unique_seq = this_person_settings['unique_seq']
                experiment.stimlist = this_person_settings['stimlist']
                experiment.stimpr = this_person_settings['stimpr']
                experiment.last_N = this_person_settings['last_N']
                experiment.last_session = this_person_settings['last_session']
                experiment.end_at = this_person_settings['end_at']
        except:
            experiment.subject_age = None
            experiment.subject_sex = None
            experiment.stim_sessionN = {}
            experiment.stimblock = {}
            experiment.stimtrial = {}
            experiment.unique_seq = None
            experiment.stimlist = []
            experiment.stimpr = []
            experiment.last_N = 0
            experiment.last_session = 0
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

            this_person_settings['unique_seq'] = experiment.unique_seq
            this_person_settings['stimlist'] = experiment.stimlist
            this_person_settings['stimpr'] = experiment.stimpr
            this_person_settings['last_N'] = experiment.last_N
            this_person_settings['last_session'] = experiment.last_session
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
                subject_list_IO.write('subject_id\tsubject_sex\tsubject_age\n')

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
            session = experiment.stim_sessionN[N]

            output_data = [str(experiment.subject_number).zfill(2),
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

        heading_list = ['subject_number',
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
                        'respKeys',
                        'respRT',
                        'tresptrig',
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
        # self.main_loop_lock = threading.Lock()

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
        # participant's unique sequence base on his number
        self.unique_seq = None
        # global trial number -> first trial of the next session mapping (e. g.{1 : 3, 2 : 3, 3 : 5, 4 : 5} - two sessions with two trials in each)
        self.end_at = None
        # global trial number -> pattern or random stimulus mapping (e. g.{1 : 'pattern', 2 : 'random', 3 : 'pattern', 4 : 'random'} - two sessions with two trials in each)
        self.stimpr = None
        # number of the last trial (it is 0 in the beggining and it is always equal with the last displayed stimulus's serial number
        self.last_N = None
        # number of the last session
        self.last_session = None
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
            settings_dialog.addField('Participant number', str(1).zfill(2))

            returned_data = settings_dialog.show()
            if settings_dialog.OK:
                subject_number = returned_data[0]
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

        if self.last_N + 1 <= self.settings.get_maxtrial('all'):
            # if self.last_N + 1 == self.settings.get_maxtrial('trainTest'):
            expstart11 = gui.Dlg(title='Starting task...')
            expstart11.addText("Already have participant's data")
            expstart11.addText('Continue from here...')
            expstart11.addText('Session: ' + str(self.stim_sessionN[self.last_N + 1]))
            # expstart11.addText('Session: ' + str(self.last_session))
            expstart11.addText('Block: ' + str(self.stimblock[self.last_N + 1]))
            expstart11.show()
            if not expstart11.OK:
                core.quit()
        else:
            expstart11 = gui.Dlg(title='Continue...')
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

        keys = [1, 2, 3, 4, 5]
        # maybe need to create a loop to iter until finds a seq that was not used yet
        if self.unique_seq is None: 
            np.random.shuffle(keys)
            self.unique_seq = keys
        else:
            keys = self.unique_seq
        
        trials = np.arange(1, self.settings.get_maxtrial('trainTest') + 2)
        half = self.settings.get_maxtrial('test')/2
        data = pd.DataFrame({'trials': trials,
                             'trial_keys': np.zeros(len(trials), dtype=int),
                             'trial_type': ['to_define']*len(trials)})


        if self.settings.current_session == 1:
            for trial in trials:
                if trial in np.arange((self.settings.trials_in_tBlock + half + 1), (len(trials) + 1), self.settings.trials_in_block):
                    data.trial_keys.at[trial] = np.random.choice(keys)
                    data.trial_type.at[trial] = 'no transition'
                elif trial in np.arange(1, (self.settings.trials_in_tBlock + 1)):
                    data.trial_type.at[trial] = 'training'
                    if data.trial_keys.at[trial-1] == keys[0]:
                        data.trial_keys.at[trial] = keys[np.random.choice([1, 2, 3, 4])]
                    elif data.trial_keys.at[trial-1] == keys[1]:
                        data.trial_keys.at[trial] = keys[np.random.choice([0, 2, 3, 4])]
                    elif data.trial_keys.at[trial-1] == keys[2]:
                        data.trial_keys.at[trial] = keys[np.random.choice([0, 1, 3, 4])]
                    elif data.trial_keys.at[trial-1] == keys[3]:
                        data.trial_keys.at[trial] = keys[np.random.choice([0, 1, 2, 4])]
                    else:
                        data.trial_keys.at[trial] = keys[np.random.choice([0, 1, 2, 3])]
                elif trial in np.arange((self.settings.trials_in_tBlock + 1), (self.settings.trials_in_tBlock + half + 1)):
                    data.trial_type.at[trial] = 'random'
                    if data.trial_keys.at[trial-1] == keys[0]:
                        data.trial_keys.at[trial] = keys[np.random.choice([1, 2, 3, 4])]
                    elif data.trial_keys.at[trial-1] == keys[1]:
                        data.trial_keys.at[trial] = keys[np.random.choice([0, 2, 3, 4])]
                    elif data.trial_keys.at[trial-1] == keys[2]:
                        data.trial_keys.at[trial] = keys[np.random.choice([0, 1, 3, 4])]
                    elif data.trial_keys.at[trial-1] == keys[3]:
                        data.trial_keys.at[trial] = keys[np.random.choice([0, 1, 2, 4])]
                    else:
                        data.trial_keys.at[trial] = keys[np.random.choice([0, 1, 2, 3])]
                else:
                    if data.trial_keys[trial-1] == keys[0]:
                        data.trial_keys.at[trial] = keys[1]
                        data.trial_type.at[trial] = 'deterministic'
                    elif data.trial_keys[trial-1] == keys[0]:
                        data.trial_keys.at[trial] = keys[1]
                        data.trial_type.at[trial] = 'deterministic'
                    elif data.trial_keys[trial-1] == keys[1]:
                        data.trial_keys.at[trial] = keys[np.random.choice([0, 2, 3, 4])]
                        data.trial_type.at[trial] = 'pseudo-random'
                    elif data.trial_keys[trial-1] == keys[2]:
                        if np.random.random() < 3/4:
                            data.trial_keys.at[trial] = keys[4]
                            data.trial_type.at[trial] = 'high_prob'
                        else:
                            data.trial_keys.at[trial] = keys[0]
                            data.trial_type.at[trial] = 'low_prob'
                    elif data.trial_keys[trial-1] == keys[3]:
                        if np.random.random() < 1/2:
                            data.trial_keys.at[trial] = keys[0]
                            data.trial_type.at[trial] = 'medium_prob'
                        else:
                            data.trial_keys.at[trial] = keys[2]
                            data.trial_type.at[trial] = 'medium_prob'
                    elif data.trial_keys.at[trial-1] == keys[4]:
                        if np.random.random() < 3/4:
                            data.trial_keys.at[trial] = keys[3]
                            data.trial_type.at[trial] = 'high_prob'
                        else:
                            data.trial_keys.at[trial] = keys[2]
                            data.trial_type.at[trial] = 'low_prob'
        else:
            for trial in trials:
                if trial in np.arange((self.settings.trials_in_tBlock + 1), (self.settings.trials_in_tBlock + half + 1), self.settings.trials_in_block):
                    data.trial_keys.at[trial] = np.random.choice(keys)
                    data.trial_type.at[trial] = 'no transition'
                elif trial in np.arange(1, (self.settings.trials_in_tBlock + 1)):
                    data.trial_type.at[trial] = 'training'
                    if data.trial_keys.at[trial-1] == keys[0]:
                        data.trial_keys.at[trial] = keys[np.random.choice([1, 2, 3, 4])]
                    elif data.trial_keys.at[trial-1] == keys[1]:
                        data.trial_keys.at[trial] = keys[np.random.choice([0, 2, 3, 4])]
                    elif data.trial_keys.at[trial-1] == keys[2]:
                        data.trial_keys.at[trial] = keys[np.random.choice([0, 1, 3, 4])]
                    elif data.trial_keys.at[trial-1] == keys[3]:
                        data.trial_keys.at[trial] = keys[np.random.choice([0, 1, 2, 4])]
                    else:
                        data.trial_keys.at[trial] = keys[np.random.choice([0, 1, 2, 3])]
                elif trial in np.arange((self.settings.trials_in_tBlock + half + 1), (len(trials) + 1)):
                    data.trial_type.at[trial] = 'random'
                    if data.trial_keys.at[trial-1] == keys[0]:
                        data.trial_keys.at[trial] = keys[np.random.choice([1, 2, 3, 4])]
                    elif data.trial_keys.at[trial-1] == keys[1]:
                        data.trial_keys.at[trial] = keys[np.random.choice([0, 2, 3, 4])]
                    elif data.trial_keys.at[trial-1] == keys[2]:
                        data.trial_keys.at[trial] = keys[np.random.choice([0, 1, 3, 4])]
                    elif data.trial_keys.at[trial-1] == keys[3]:
                        data.trial_keys.at[trial] = keys[np.random.choice([0, 1, 2, 4])]
                    else:
                        data.trial_keys.at[trial] = keys[np.random.choice([0, 1, 2, 3])]
                else:
                    if data.trial_keys[trial-1] == keys[0]:
                        data.trial_keys.at[trial] = keys[1]
                        data.trial_type.at[trial] = 'deterministic'
                    elif data.trial_keys[trial-1] == keys[0]:
                        data.trial_keys.at[trial] = keys[1]
                        data.trial_type.at[trial] = 'deterministic'
                    elif data.trial_keys[trial-1] == keys[1]:
                        data.trial_keys.at[trial] = keys[np.random.choice([0, 2, 3, 4])]
                        data.trial_type.at[trial] = 'pseudo-random'
                    elif data.trial_keys[trial-1] == keys[2]:
                        if np.random.random() < 3/4:
                            data.trial_keys.at[trial] = keys[4]
                            data.trial_type.at[trial] = 'high_prob'
                        else:
                            data.trial_keys.at[trial] = keys[0]
                            data.trial_type.at[trial] = 'low_prob'
                    elif data.trial_keys[trial-1] == keys[3]:
                        if np.random.random() < 1/2:
                            data.trial_keys.at[trial] = keys[0]
                            data.trial_type.at[trial] = 'medium_prob'
                        else:
                            data.trial_keys.at[trial] = keys[2]
                            data.trial_type.at[trial] = 'medium_prob'
                    elif data.trial_keys.at[trial-1] == keys[4]:
                        if np.random.random() < 3/4:
                            data.trial_keys.at[trial] = keys[3]
                            data.trial_type.at[trial] = 'high_prob'
                        else:
                            data.trial_keys.at[trial] = keys[2]
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


    def calculate_stim_properties(self, session_num):
        """Calculate all variables used during the trials before the presentation starts."""

        (self.stimlist, self.stimpr) = self.open_sequence()

        all_trial_Nr = 0
        block_num = 0

        sessionsstarts = self.settings.get_session_starts()
        # for trial_num in range(1, self.settings.get_maxtrial('trainTest') + 1):
        #     for session_num in range(1, len(sessionsstarts)+1):
        #         if trial_num >= sessionsstarts[session_num - 1] and trial_num < sessionsstarts[session_num]:
        #             self.stim_sessionN[trial_num] = session_num
        #             self.end_at[trial_num] = sessionsstarts[session_num]
        
        for trial_num in range(1, self.settings.get_maxtrial('trainTest') + 1):
            self.stim_sessionN[trial_num] = session_num
            self.end_at[trial_num] = sessionsstarts[1]
        
        current_trial_num = 0
        
        # training
        for train in range(1, self.settings.trials_in_tBlock + 1):
            current_trial_num += 1
            all_trial_Nr += 1

            self.stimtrial[all_trial_Nr] = current_trial_num
            self.stimblock[all_trial_Nr] = 0
        
        # test
        for block in range(1, self.settings.blocks_in_session + 1):
            block_num += 1

            for test in range(1, self.settings.trials_in_block + 1):
                current_trial_num += 1
                all_trial_Nr += 1
                self.stimtrial[all_trial_Nr] = current_trial_num
                self.stimblock[all_trial_Nr] = block_num

    def pixel_to_degrees(self, size_px):
        """
            h: height of the monitor in cm
            d: distance from the participant to the monitor in cm
            r: vertical resolution of the monitor in pixels
            size_px: size in pixels
        """
        
        h = self.settings.monitor_height
        d = self.settings.monitor_distance
        r = screen_width
        
        # calculate the number of degrees that correspond to a single pixel
        deg_per_px = degrees(atan2(.5 * h, d)) / (.5 * r)
        
        size_in_deg = size_px * deg_per_px
        
        return size_in_deg


    def participant_id(self):
        """Find out the current subject and read subject settings / progress if he/she already has any data."""

        self.show_subject_identification_dialog()

        # unique subject ID
        subject_id = str(self.subject_number).zfill(2)

        # init subject data handler with the right file paths
        all_settings_file_path = os.path.join(self.workdir_path, "settings", subject_id)
        all_IDs_file_path = os.path.join(self.workdir_path, "settings", "participant_settings")
        sequence_file_path = os.path.join(self.workdir_path, "sequences",
                                          str(self.subject_number) + '_seq' + str(self.settings.current_session) + '.csv')
        subject_list_file_path = os.path.join(self.workdir_path, "settings",
                                            "participants_in_experiment.csv")
        output_file_path = os.path.join(self.workdir_path, "logs", subject_id + '_log.csv')
        self.person_data = PersonDataHandler(subject_id, all_settings_file_path,
                                            all_IDs_file_path, sequence_file_path, subject_list_file_path,
                                            output_file_path)

        # try to load settings and progress for the given subject ID
        self.person_data.load_person_settings(self)

        if self.last_N > 0:
            # the current subject already started the experiment
            try:
                self.show_subject_continuation_dialog()
                self.open_sequence()
            except:
                self.last_N = 0
                self.open_sequence()
            self.calculate_stim_properties(self.settings.current_session)
        # we have a new subject
        else:
            # ask about the pattern codes used in the different sessions
            self.show_subject_attributes_dialog()
            # update participant attribute files
            self.person_data.update_all_subject_attributes_files(self.subject_sex, self.subject_age)
            # create sequence for current session
            self.open_sequence()
            # calculate stimulus properties for the experiment
            self.calculate_stim_properties(self.settings.current_session)
            # save data of the new subject
            self.person_data.save_person_settings(self)

    def monitor_settings(self):
        """Specify monitor settings."""

        # use default screen resolution
        screen = pyglet.canvas.get_display().get_default_screen()
        self.mymonitor = monitors.Monitor('myMon', distance=80)
        self.mymonitor.setSizePix([screen.width, screen.height])
        # need to set monitor width in cm to be able to use cm unit for stimulus
        self.mymonitor.setWidth(self.settings.monitor_width)
        self.mymonitor.saveMon()

    def EL_init(self):
        """Connect to the EyeLink Host PC.
        
        The Host IP address, by default, is "100.1.1.1".
        the "el_tracker" objected created here can be accessed through the Pylink
        Set the Host PC address to "None" (without quotes) to run the script in "Dummy Mode"""
        
        try:
            self.el_tracker = pylink.EyeLink("100.1.1.1") # enter the host pc ip adress, must be connected to with an ethernet cable
        except RuntimeError as error:
            print("ERROR:", error)
            core.quit()
            sys.exit()
    
    def open_edf_file(self):
        """Open an EDF data file on the Host PC"""
        
        # edf_file = f"eL_file_{self.subject_number}_{self.settings.current_session}.edf"
        edf_file = f"eL_file.edf"
        try:
            self.el_tracker.openDataFile(edf_file)
        except RuntimeError as err:
            print('ERROR:', err)
            # close the link if we have one open
            if self.el_tracker.isConnected():
                self.el_tracker.close()
            core.quit()
            sys.exit()
        preamble_text = 'SUBJECT ID: %s' % self.subject_number
        self.el_tracker.sendCommand("add_file_preamble_text '%s'" % preamble_text)

    
    def EL_config(self):
        """ Configure the tracker"""
        
        self.el_tracker.setOfflineMode()
        vstr = self.el_tracker.getTrackerVersionString()
        eyelink_ver = int(vstr.split()[-1].split('.')[0])
        print('Running experiment on %s, version %d' % (vstr, eyelink_ver))
        
        # File and Link data control
        # what eye events to save in the EDF file, include everything by default
        file_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT'
        # what eye events to make available over the link, include everything by default
        link_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON,FIXUPDATE,INPUT'
        # what sample data to save in the EDF data file and to make available
        # over the link, include the 'HTARGET' flag to save head target sticker
        # data for supported eye trackers
        if eyelink_ver > 3:
            file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,HTARGET,GAZERES,BUTTON,STATUS,INPUT'
            link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,HTARGET,STATUS,INPUT'
        else:
            file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,GAZERES,BUTTON,STATUS,INPUT'
            link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT'
        self.el_tracker.sendCommand("file_event_filter = %s" % file_event_flags)
        self.el_tracker.sendCommand("file_sample_data = %s" % file_sample_flags)
        self.el_tracker.sendCommand("link_event_filter = %s" % link_event_flags)
        self.el_tracker.sendCommand("link_sample_data = %s" % link_sample_flags)
        # Optional tracking parameters
        # Sample rate, 250, 500, 1000, or 2000, check your tracker specification
        # if eyelink_ver > 2:
        #     self.el_tracker.sendCommand("sample_rate 1000")
        # Choose a calibration type, H3, HV3, HV5, HV13 (HV = horizontal/vertical),
        self.el_tracker.sendCommand("calibration_type = HV9")
        # Set a gamepad button to accept calibration/drift check target
        # You need a supported gamepad/button box that is connected to the Host PC
        self.el_tracker.sendCommand("button_function 5 'accept_target_fixation'")

        # Optional -- Shrink the spread of the calibration/validation targets
        # if the default outermost targets are not all visible in the bore.
        # The default <x, y display proportion> is 0.88, 0.83 (88% of the display
        # horizontally and 83% vertically)
        self.el_tracker.sendCommand('calibration_area_proportion 0.88 0.83')
        self.el_tracker.sendCommand('validation_area_proportion 0.88 0.83')    

    def EL_calibration(self):
        """ Set up a graphic environment for calibration/"""
                
        # Write a DISPLAY_COORDS message to the EDF file
        # Data Viewer needs this piece of info for proper visualization, see Data
        # Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
        dv_coords = "DISPLAY_COORDS  0 0 %d %d" % (screen_width - 1, screen_height - 1)
        self.el_tracker.sendMessage(dv_coords)

        # Configure a graphics environment (genv) for tracker calibration
        genv = EyeLinkCoreGraphicsPsychoPy(self.el_tracker, self.mywindow)
        print(genv)  # print out the version number of the CoreGraphics library

        # Set background and foreground colors for the calibration target
        # in PsychoPy, (-1, -1, -1)=black, (1, 1, 1)=white, (0, 0, 0)=mid-gray
        foreground_color = (-1, -1, -1)
        # background_color = self.mywindow.color
        background_color = (1, 1, 1)
        genv.setCalibrationColors(foreground_color, background_color)

        # Set up the calibration target
        #
        # The target could be a "circle" (default), a "picture", a "movie" clip,
        # or a rotating "spiral". To configure the type of calibration target, set
        # genv.setTargetType to "circle", "picture", "movie", or "spiral"
        
        genv.setTargetType('picture')
        genv.setPictureTarget(os.path.join('images', 'fixTarget.bmp'))

        # Configure the size of the calibration target (in pixels)
        # this option applies only to "circle" and "spiral" targets
        # genv.setTargetSize(24)

        # Beeps to play during calibration, validation and drift correction
        # parameters: target, good, error
        #     target -- sound to play when target moves
        #     good -- sound to play on successful operation
        #     error -- sound to play on failure or interruption
        # Each parameter could be ''--default sound, 'off'--no sound, or a wav file
        genv.setCalibrationSounds('', '', '')

        # Request Pylink to use the PsychoPy window we opened above for calibration
        pylink.openGraphicsEx(genv)
        
        self.el_tracker.doTrackerSetup()
        
    def EL_abort(self):
        """Ends recording """

        el_tracker = pylink.getEYELINK()

        # Stop recording
        if el_tracker.isRecording():
            # add 100 ms to catch final trial events
            pylink.pumpDelay(100)
            el_tracker.stopRecording()
                    
    def EL_disconnect(self):
        
        self.el_tracker = pylink.getEYELINK()
        
        if self.el_tracker.isConnected():
            
            # Put tracker in Offline mode
            self.el_tracker.setOfflineMode()

            # Clear the Host PC screen and wait for 500 ms
            self.el_tracker.sendCommand('clear_screen 0')
            pylink.msecDelay(500)

            # Close the edf data file on the Host
            self.el_tracker.closeDataFile()

            # Show a file transfer message on the screen
            self.print_to_screen('EDF data is transferring from EyeLink Host PC...')

            # Download the EDF data file from the Host PC to a local data folder
            # parameters: source_file_on_the_host, destination_file_on_local_drive
            # edf_file = f"eL_{self.subject_number}_{self.settings.current_session}.edf"
            edf_file = "eL_file.edf"
            # local_edf = os.path.join(f"local_eL_{self.subject_number}_{self.settings.current_session}.edf")
            local_edf = os.path.join("%s.edf" % self.subject_number)
            try:
                self.el_tracker.receiveDataFile(edf_file, local_edf)
            except RuntimeError as error:
                print('ERROR:', error)

            # Close the data file
            self.el_tracker.closeDataFile()
            
            # Close the link to the tracker.
            self.el_tracker.close()
            
    def in_or_out(self, eye_used, old_sample, new_sample, in_hit_region, minimum_duration, gaze_start):
        done = False
        s = sound.Sound('A', secs=.5, stereo=True, hamming=True, volume=1.0)
        while not done:
            # s.play()
            # Do we have a sample in the sample buffer?
            # and does it differ from the one we've seen before?
            new_sample = self.el_tracker.getNewestSample()
            if new_sample is not None:
                if old_sample is not None:
                    if new_sample.getTime() != old_sample.getTime():
                        # check if the new sample has data for the eye
                        # currently being tracked; if so, we retrieve the current
                        # gaze position and PPD (how many pixels correspond to 1
                        # deg of visual angle, at the current gaze position)
                        if eye_used == 1 and new_sample.isRightSample():
                            g_x, g_y = new_sample.getRightEye().getGaze()
                        if eye_used == 0 and new_sample.isLeftSample():
                            g_x, g_y = new_sample.getLeftEye().getGaze()

                        # break the while loop if the current gaze position is
                        # in a 128 x 128 pixels region around the screen centered
                        gaze_start = core.getTime()
                        fix_x, fix_y = (screen_width/2.0, screen_height/2.0)
                        if not (fabs(g_x - fix_x) < 64 and fabs(g_y - fix_y) < 64):
                            gaze_dur = core.getTime() - gaze_start
                            if gaze_dur > minimum_duration:
                                s.play()
                        else:  # gaze outside the hit region, reset variables
                            s.stop()
                            done = True
                # update the "old_sample"
                old_sample = new_sample

    def print_to_screen(self, mytext):
        """Display any string on the screen."""

        xtext = visual.TextStim(self.mywindow, text=mytext,
                                units="cm", height=0.7, wrapWidth=20,
                                color="black")
        xtext.draw()
        self.mywindow.flip()


    def frame_check(self):  
        """Measure the frame rate, using different measurements."""

        self.print_to_screen("Chargement...")
        core.wait(2)

        ms_per_frame = self.mywindow.getMsPerFrame(nFrames=120)
        self.frame_time = ms_per_frame[0]
        self.frame_sd = ms_per_frame[1]
        self.frame_rate = self.mywindow.getActualFrameRate()

    def prog_bar(self, N):
        
        # width = self.pixel_to_degrees(1000)
        # height = self.pixel_to_degrees(150)
        progress = (N/self.settings.get_maxtrial('test'))*1000
        # prog = self.pixel_to_degrees(progress)
        
        bar_outline = visual.Rect(win=self.mywindow, units='pix',
                            pos=(-500, -screen_height/2),
                            size=(1000, 20),
                            fillColor=None,
                            lineColor='black', lineWidth=1)
        bar = visual.Rect(win=self.mywindow, units='pix',
                    pos=(-500, -screen_height/2),
                    size=(progress, 20),
                    fillColor='blue',
                    lineWidth=0)
        
        bar.draw()
        bar_outline.draw()
        
    # def drawBar(self, N):
    #     progress = (N/self.settings.get_maxtrial('test'))*100
    #     bar = widgets.ProgressBar(title='prog_bar', default=0, width=progress,
    #                               box_background_color='white',
    #                               box_border_color='black', box_border_width=2,
    #                               box_margin=(-500, -screen_width/2),
    #                               box_progress_color='green',
    #                               progress_text_enabled=True, progress_text_align='CENTER')
        

    def show_feedback(self, N, responses_in_block, accs_in_block, RT_all_list):
        """ Display feedback in the end of the blocks, showing some data about speed and accuracy."""

        acc_for_the_whole = 100 * float(responses_in_block - sum(accs_in_block)) / responses_in_block
        acc_for_the_whole_str = str(acc_for_the_whole)[0:5].replace('.', ',')

        rt_mean = float(sum(RT_all_list)) / len(RT_all_list)
        rt_mean_str = str(rt_mean)[:5].replace('.', ',')
        
        progress = ((N-self.settings.trials_in_tBlock)/self.settings.get_maxtrial('test'))*1000
        percent = round((progress/10))
        text = f"{percent}%"
        
        bar_outline = visual.Rect(win=self.mywindow, units='pix',
                            pos=(0, -300),
                            size=(1004, 65),
                            fillColor=None,
                            lineColor='black', lineWidth=3)
        bar = visual.Rect(win=self.mywindow, units='pix',
                    pos=((-500+progress/2), -300),
                    size=(progress, 60),
                    fillColor='green',
                    lineWidth=0)
        completed = visual.TextStim(self.mywindow, text=text,
                                units="pix", height=50, wrapWidth=20,
                                anchorHoriz='center',
                                pos=(0, -300),
                                color="black")
    
        bar.draw()
        bar_outline.draw()
        completed.draw()
        
        whatnow = self.instructions.feedback_RT_acc(
            rt_mean, rt_mean_str, acc_for_the_whole, acc_for_the_whole_str, self.mywindow, self.settings)

    def wait_for_response_1(self, expected_response, response_clock, eye_used, old_sample, new_sample, in_hit_region, minimum_duration, gaze_start):
        """ for eyetracker """
        press = []
        in_hit_region = None
        s = sound.Sound('A', secs=.5, stereo=True, hamming=True, volume=1.0)
        while len(press) == 0:
            new_sample = self.el_tracker.getNewestSample()
            if new_sample is not None:
                if old_sample is not None:
                    if new_sample.getTime() != old_sample.getTime():
                        # check if the new sample has data for the eye
                        # currently being tracked; if so, we retrieve the current
                        # gaze position and PPD (how many pixels correspond to 1
                        # deg of visual angle, at the current gaze position)
                        if eye_used == 1 and new_sample.isRightSample():
                            g_x, g_y = new_sample.getRightEye().getGaze()
                        if eye_used == 0 and new_sample.isLeftSample():
                            g_x, g_y = new_sample.getLeftEye().getGaze()
                        # break the while loop if the current gaze position is
                        # in a 128 x 128 pixels region around the screen centered
                        fix_x, fix_y = (screen_width/2.0, screen_height/2.0)
                        if not (fabs(g_x - fix_x) < 64 and fabs(g_y - fix_y) < 64):
                            # gaze_start = core.getTime()
                            # gaze_dur = core.getTime() - gaze_start
                            # if gaze_dur > minimum_duration:
                            if in_hit_region:
                                if gaze_start == -1:
                                    gaze_start = core.getTime()
                                    in_hit_region = False
                            if not in_hit_region:
                                gaze_dur = core.getTime() - gaze_start
                                if gaze_dur > minimum_duration:
                                    s.play()
                        else:
                            s.stop()
                            in_hit_region = True
                            gaze_start = -1
                # update the "old_sample"
                old_sample = new_sample
            press = event.getKeys(keyList=self.settings.get_key_list(), timeStamped=response_clock)
            # self.in_or_out(eye_used, old_sample, new_sample, in_hit_region, minimum_duration, gaze_start)
        if press[0][0] == 'q':
            return (-1, press[0][1])
        return (self.pressed_dict[press[0][0]], press[0][1])

    def wait_for_response_3(self, expected_response,  response_clock):
        """ without eyetracking """
        
        press = []
        while len(press) == 0:
            press = event.getKeys(keyList=self.settings.get_key_list(), timeStamped=response_clock)
        print(press)
        if press[0][0] == 'q':
            return (-1, press[0][1])
        return (self.pressed_dict[press[0][0]], press[0][1])

    def wait_for_response_2(self, tStart, k=0, r=0, t=0): # create a while loop and insert eyetracking function
        """ with response box, to merge with wait_for_response_1 """
        
        key_from_serial2 = str(port_s.readline())[2:-1]
        if len(key_from_serial2) > 0:
            key_from_serial2 = key_from_serial2[3]
            if ((key_from_serial2 == '1') or (key_from_serial2 == '2')):
                k = key_from_serial2 # just the last key pressed
                r = ptb.GetSecs() - tStart
                t = ptb.GetSecs()
                port.setData(50) # response ppt
        return k, r, t

    def send_trigger(self, N, trigg_value):    
        port.setData(trigg_value)
        time.sleep(.005)
        port.setData(0)
                
    def quit_presentation(self):
        self.print_to_screen("Exiting...\nSaving data...")
        self.person_data.append_to_output_file('userquit')
        core.wait(3)
        if eyetracking:
            self.EL_disconnect()
        core.quit()
        
    def fixation_cross(self):
        
        size = self.pixel_to_degrees(128)
        
        outer = visual.Circle(win=self.mywindow, units='deg', radius=size,
                              color=(0,0,0), opacity=1)
        inner = visual.Circle(win=self.mywindow, units='deg', radius=size/2,
                              color=(0,0,0), opacity=1)
        cross = visual.ShapeStim(
            win=self.mywindow, vertices='cross',
            units='deg', size=(size, size),
            ori=0.0, pos=(0, 0), anchor='center',
            lineWidth=1.0, color=(255, 255, 255),
            opacity=1, depth=-8.0, interpolate=True)
        
        outer.draw()
        cross.draw()
        inner.draw()
    
    def resting_period(self, outer, cross, inner, experiment):
        """Resting time with eyes closed."""

        self.print_to_screen("Fermez vos yeux")
        if not meg_session:
            core.wait(2)
        # wait for closing of eyes with eye-tracker
        # tempkey = event.waitKeys(keyList=experiment.get_key_list())

        s = sound.Sound('A', secs=.5, stereo=True, hamming=True, volume=1.0)

        # if experiment.key_quit in tempkey:
        #     self.quit_presentation()
        # else:
            # self.mywindow.flip()
        rest_time = core.CountdownTimer(self.settings.rest_time)
        while rest_time.getTime() > 1:
            outer.draw()
            cross.draw()
            inner.draw()
            self.mywindow.flip()
        if not debug_mode:
            s.play()
        while rest_time.getTime() > 0:
            outer.draw()
            cross.draw()
            inner.draw()
            self.mywindow.flip()
        
    def close_to_break(self, outer, cross, inner, experiment, 
                       eye_used, old_sample, new_sample, minimum_duration, gaze_start):
        closed = False
        s = sound.Sound('A', secs=.5, stereo=True, hamming=True, volume=1.0)
        in_hit_region = None
        
        while not closed:
            self.print_to_screen("Fermez vos yeux pour lancer la pause")
            
            # timer = core.CountdownTimer(10)
            # while timer.getTime() > 0:
    
            new_sample = self.el_tracker.getNewestSample()
            if new_sample is not None:
                if old_sample is not None:
                    if new_sample.getTime() != old_sample.getTime():
                        if eye_used == 1 and new_sample.isRightSample():
                            g_x, g_y = new_sample.getRightEye().getGaze()
                        if eye_used == 0 and new_sample.isLeftSample():
                            g_x, g_y = new_sample.getLeftEye().getGaze()
                        print('x:', g_x, 'y:', g_y)
                        # fix_x, fix_y = (screen_width/2.0, screen_height/2.0)
                        # if (fabs(g_x - fix_x) < 64 and fabs(g_y - fix_y) < 64):
                        if (g_x == -32768.0 or g_y == -32768.0):
                            if not in_hit_region:
                                if gaze_start == -1:
                                    gaze_start = core.getTime()
                                    in_hit_region = True
                            # check the gaze duration and fire
                            if in_hit_region:
                                gaze_dur = core.getTime() - gaze_start
                                if gaze_dur > minimum_duration:
                                    closed = True
                                    # break
                            else:
                                in_hit_region = False
                                gaze_start = -1
                old_sample = new_sample
        
        rest_time = core.CountdownTimer(self.settings.rest_time)
        while rest_time.getTime() > 1:
            outer.draw()
            cross.draw()
            inner.draw()
            self.mywindow.flip()
        if not debug_mode:
            s.play()
        while rest_time.getTime() > 0:
            outer.draw()
            cross.draw()
            inner.draw()
            self.mywindow.flip()
    
    def set_audio(self):
        prefs.hardware['audioLib'] = 'PTB'
        prefs.hardware['audioDevice'] = 'Haut-parleurs (Sound Blaster Audigy 5/Rx)'
        prefs.hardware['audioLatencyMode'] = 4

    def circle_bg(self, stimbg, dict_pos):
        """ Draw empty stimulus circles. """

        for i in range(1, 6):
            stimbg.setPos(dict_pos[i])
            stimbg.draw()

    def super_tutorial(self, sizep, outer, inner, cross):
                        
        trial_clock = core.Clock()
        
        dict_pos = {1: (-100, -350),
                    2: (0, -350),
                    3: (100, -350),
                    4: (200, -350),
                    5: (-200, -400)}
                
        n = 1
        
        stim = visual.ImageStim(win=self.mywindow, image=self.image_dict[n],
                                pos=(0,0), units='deg', size=(sizep, sizep), opacity=0)
        circle_bg = visual.Circle(win=self.mywindow, radius=25, units="pix",
                                  fillColor=None, lineColor='black', lineWidth=5)
        correct = visual.Circle(win=self.mywindow, radius=24, units="pix", fillColor='green')
        wrong = visual.Circle(win=self.mywindow, radius=24, units="pix", fillColor='red', opacity=.6)
        
        tuto = [1, 2, 3, 4, 5,
                1, 2, 3, 4, 5,
                1, 2, 3, 4, 5,
                3, 5, 2, 1, 4,
                2, 4, 1, 5, 1,
                5, 1, 4, 2, 3]
        dict_t = {i+1 : tuto[i] for i in range(0, len(tuto))}
        
        while True:
            outer.draw()
            cross.draw()
            inner.draw()
            self.circle_bg(circle_bg, dict_pos)
            self.mywindow.flip()
            stim.draw()

            while True:
                stim = visual.ImageStim(win=self.mywindow, image=self.image_dict[dict_t[n]],
                                        pos=(0,0), units='deg', size=(sizep, sizep), opacity=1)
                correct.setPos(dict_pos[dict_t[n]])

                stim.draw()
                outer.draw()
                cross.draw()
                inner.draw()
                self.circle_bg(circle_bg, dict_pos)
                correct.draw()
                self.mywindow.flip()
                
                response = self.wait_for_response_3(dict_t[n], trial_clock)[0]
                if response == dict_t[n]:
                    stim.setOpacity(0)
                    self.mywindow.flip()
                    n += 1
                    break
                elif response == self.settings.key_quit:
                    core.quit()
                else:
                    wrong.setPos(dict_pos[response])
                    wrong.draw()
            
            if n == self.settings.trials_in_pretrain+1:
                break
        
        self.mywindow.flip()
        self.print_to_screen("Bravo vous avez terminé le tutoriel.\n\n Appuyez sur Y pour lancer l'entraînement.")
        core.wait(1)
        press = event.waitKeys(keyList=self.settings.get_key_list())
        if press in self.settings.get_key_list():
            self.mywindow.flip()
        elif self.settings.key_quit in press:
            core.quit()


    def presentation(self):
        """The real experiment happens here. This method displays the stimulus window and records the RTs."""

        size = self.pixel_to_degrees(128)
        sizep = self.pixel_to_degrees(254)

        # stimulus init
        stim = visual.ImageStim(win=self.mywindow, image=self.image_dict[self.stimlist[1]],
                                pos=(0,0), units='deg', size=(sizep, sizep), opacity=0)


        # fixation cross init
        fixation_cross = visual.TextStim(win=self.mywindow, text="+",
                                              units="cm", height=1,
                                              color='black', opacity=1,
                                              pos=(0,0))
        # (outer, cross, inner) = self.fixation_cross()
        
        
        outer = visual.Circle(win=self.mywindow, units='deg', radius=size/6,
                              fillColor='black', opacity=.7)
        inner = visual.Circle(win=self.mywindow, units='deg', radius=size/36,
                              fillColor='black', opacity=.7)
        cross = visual.ShapeStim(
            win=self.mywindow, vertices='cross',
            units='deg', size=(size/3, size/3),
            ori=0.0, pos=(0, 0),
            lineWidth=.5,  lineColor='white', fillColor='white',
            opacity=.7, depth=-8.0, interpolate=True)
        
        # Photodiode configuration
        pixel = visual.Rect(win=self.mywindow, units='pix',
                            pos=(0, screen_height/2),
                            size=(screen_width, 100),
                            fillColor='black', lineColor='black')
        pixel.setAutoDraw(True) # set to True/False to activate/deactivate

        # feedbacks during training block
        green = visual.Circle(win=self.mywindow, units='deg', radius=sizep/2,
                            lineColor='green', fillColor='green',
                            opacity=.50)
        red = visual.Circle(win=self.mywindow, units='deg', radius=sizep/2,
                            lineColor='red', fillColor='red',
                            opacity=.50)
        
        # trigger codes
        d = {'training': [1, 2, 3, 4, 5],
             'no transition': [11, 12, 13, 14, 15],
             'random': [21, 22, 23, 24, 25],
             'deterministic': [31, 32, 33, 34, 35],
             'high_prob': [41, 42, 43, 44, 45],
             'medium_prob': [51, 52, 53, 54, 55],
             'low_prob': [61, 62, 63, 64, 65],
             'pseudo-random': [71, 72, 73, 74, 75]}

        # eye-tracking related
        new_sample = None
        old_sample = None
        in_hit_region = False
        minimum_duration = .6
        gaze_start = -1

        stim_RSI = 0.0
        N = self.last_N + 1

        responses_in_block = 0
        accs_in_block = []

        num_of_random = 0
        num_of_deter = 0
        num_of_high = 0
        num_of_low = 0

        RT_random_list = []
        RT_deter_list = []
        RT_high_list = []
        RT_low_list = []
        RT_all_list = []

        err_random = 0
        err_deter = 0
        err_high = 0
        err_low = 0
        err_all = 0

        RSI = core.StaticPeriod(screenHz=self.frame_rate)
        RSI_clock = core.Clock()
        trial_clock = core.Clock()

        first_trial_in_block = True

        self.trial_phase = "before_stimulus"
        self.last_RSI = -1
        
        if eyetracking:
            self.EL_calibration()

        # show instructions or continuation message
        if N in self.settings.get_session_starts():
            self.print_to_screen("Bienvenue !")
            core.wait(5)
            self.mywindow.flip()
            
            # starting resting state
            if resting_state:
                self.print_to_screen("Fixez la croix de fixation.")
                core.wait(2)
                self.mywindow.flip()
            
                timer = core.CountdownTimer(self.settings.rs_time)
                while timer.getTime() > 0:
                    outer.draw()
                    cross.draw()
                    inner.draw()
                    self.mywindow.flip()
            
            self.instructions.show_instructions(self)
            core.wait(1)
            press = event.waitKeys(keyList=self.settings.get_key_list())
            if press in self.settings.get_key_list():
                self.mywindow.flip()
            elif self.settings.key_quit in press:
                core.quit()

            if tutorial:
                self.super_tutorial(sizep, outer, inner, cross)
        else:
            self.instructions.show_unexp_quit(self)
        
        if eyetracking:
            self.el_tracker = pylink.getEYELINK()
            self.el_tracker.setOfflineMode()

            try:
                self.el_tracker.startRecording(1, 1, 1, 1)
            except RuntimeError as error:
                print("ERROR:", error)
                return pylink.TRIAL_ERROR
            
            # Allocate some time for the tracker to cache some samples
            pylink.pumpDelay(100)
            
            # determine which eye(s) is/are available
            # 0- left, 1-right, 2-binocular
            eye_used = self.el_tracker.eyeAvailable()
            if eye_used == 1:
                self.el_tracker.sendMessage("EYE_USED 1 RIGHT")
            elif eye_used == 0 or eye_used == 2:
                self.el_tracker.sendMessage("EYE_USED 0 LEFT")
                eye_used = 0
            else:
                print("Error in getting the eye information!")
                return pylink.TRIAL_ERROR
        
        RSI.start(self.settings.RSI_time)

        while True:
            
            stim.draw()
            # fixation_cross.draw()
            outer.draw()
            cross.draw()
            inner.draw()

            # if eyetracking:
            #     self.in_or_out(eye_used, old_sample, new_sample, in_hit_region, minimum_duration, gaze_start)
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
                
                tStart = ptb.GetSecs()
                tresptrig = 0
                respRT = 0
                respKeys = None

                stim = visual.ImageStim(win=self.mywindow, image=self.image_dict[self.stimlist[N]],
                                        pos=(0,0), units='deg', size=(sizep, sizep), opacity=1)
                stim.draw()
                pixel.setAutoDraw(False)
                # fixation_cross.draw()
                outer.draw()
                cross.draw()
                inner.draw()
                trigg_value = d[self.stimpr[N]][self.stimlist[N]-1]
                self.mywindow.flip()
                if meg_session:
                    self.send_trigger(N, trigg_value)
                if cycle == 1: # check next time if 0 or 1
                    if first_trial_in_block:
                        stim_RSI = 0.0
                    else:
                        stim_RSI = RSI_clock.getTime()

                with self.shared_data_lock:
                    self.trial_phase = "stimulus_on_screen"
                    self.last_RSI = stim_RSI

                if cycle == 1:
                    trial_clock.reset()
                if eyetracking:
                    (response, time_stamp) = self.wait_for_response_1(self.stimlist[N], trial_clock, eye_used, old_sample, new_sample, in_hit_region, minimum_duration, gaze_start)
                else:
                    (response, time_stamp) = self.wait_for_response_3(self.stimlist[N], trial_clock)

                # if meg_session:
                #     (respKeys, respRT, tresptrig) = self.wait_for_response_2(tStart)
                
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
                # elif str(respKeys) == str(self.stimlist[N]):
                    if meg_session:
                        port.setData(202) # trigger if good response
                        time.sleep(.005)
                        port.setData(0)
                    # start of the RSI timer and offset of the stimulus
                    stim.setOpacity(0)
                    pixel.setAutoDraw(True)
                    stim.draw()
                    self.mywindow.flip()
                    RSI_clock.reset()
                    RSI.start(self.settings.RSI_time)
                    stimACC = 0
                    accs_in_block.append(0)
                    if self.stimpr[N] == 'training':
                        timer = core.CountdownTimer(.2)
                        while timer.getTime() > 0:
                            # fixation_cross.draw()
                            outer.draw()
                            cross.draw()
                            inner.draw()
                            green.draw()
                            self.mywindow.flip()
                    elif self.stimpr[N] == 'random':
                        num_of_random += 1
                        RT_random_list.append(stimRT)
                    elif self.stimpr[N] == 'deterministic':
                        num_of_deter += 1
                        RT_deter_list.append(stimRT)
                    elif self.stimpr[N] == 'high_prob':
                        num_of_high += 1
                        RT_high_list.append(stimRT)
                    elif self.stimpr[N] == 'low_prob':
                        num_of_low += 1
                        RT_low_list.append(stimRT)
                    RT_all_list.append(stimRT)

                # wrong response --> let's wait for the next response
                else:
                    if meg_session:
                        port.setData(404) # trigger if bad response
                        time.sleep(.005)
                        port.setData(0)
                    stimACC = 1
                    accs_in_block.append(1)
                    if self.stimpr[N] == 'training':
                        timer = core.CountdownTimer(.2)
                        while timer.getTime() > 0:
                            # fixation_cross.draw()
                            outer.draw()
                            cross.draw()
                            inner.draw()
                            red.draw()
                            self.mywindow.flip()
                    elif self.stimpr[N] == 'random':
                        num_of_random += 1
                        RT_random_list.append(stimRT)
                        err_random += 1
                    elif self.stimpr[N] == 'deterministic':
                        num_of_deter += 1
                        RT_deter_list.append(stimRT)
                        err_deter += 1
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
                                                                stimRT, stimACC, response, respKeys, respRT, tresptrig])

                if stimACC == 0:
                    if eyetracking:
                        self.el_tracker.sendMessage('Trial #%d' %N)
                    N += 1
                    first_trial_in_block = False
                    break

            # resting period only
            if N in self.settings.get_block_starts() and N not in self.settings.get_fb_block():

                with self.shared_data_lock:
                    self.last_N = N - 1
                    self.trial_phase = "before stimulus"
                    self.last_RSI = - 1

                if eyetracking:
                    self.close_to_break(outer, cross, inner, self.settings, eye_used, old_sample, new_sample, minimum_duration, gaze_start)
                    core.wait(2)
                else:
                    self.resting_period(outer, cross, inner, self.settings)
                    core.wait(2)
                self.person_data.flush_data_to_output(self)
                self.person_data.save_person_settings(self)

                first_trial_in_block = True

            # resting period and feedback
            if N in self.settings.get_fb_block()[1:]:

                with self.shared_data_lock:
                    self.last_N = N - 1
                    self.trial_phase = "before stimulus"
                    self.last_RSI = - 1

                if eyetracking:
                    self.close_to_break(outer, cross, inner, self.settings, eye_used, old_sample, new_sample, minimum_duration, gaze_start)
                else:
                    self.resting_period(outer, cross, inner, self.settings)
                if meg_session:
                    # stop MEG recordings for recalibration
                    time.sleep(2)
                    port.setData(253)
                    time.sleep(.005)
                    port.setData(0)
                self.person_data.flush_data_to_output(self)
                self.person_data.save_person_settings(self)

                if meg_session:
                    self.show_feedback(N, responses_in_block, accs_in_block, RT_all_list)
                    press = event.waitKeys(keyList=self.settings.key_resume)
                    if self.settings.key_resume in press:
                        # restart the MEG recordings
                        port.setData(0)
                        time.sleep(.005)
                        port.setData(252)
                        time.sleep(.005)
                        port.setData(0)
                        self.mywindow.flip()
                    self.print_to_screen('Appuyez sur une touche pour reprendre.')
                    press_1 = event.waitKeys(keyList=self.settings.get_key_list())
                    if press_1 in self.settings.get_key_list():
                        self.mywindow.flip()
                else:
                    timer = core.CountdownTimer(self.settings.rest_time+3)
                    while timer.getTime() > 0:
                        self.show_feedback(N, responses_in_block, accs_in_block, RT_all_list)
                    self.print_to_screen('Appuyez sur une Y pour reprendre.')
                    press_1 = event.waitKeys(keyList=self.settings.get_key_list())
                    if press_1 in self.settings.get_key_list():
                        self.mywindow.flip()

                outer.draw()
                cross.draw()
                inner.draw()
                self.mywindow.flip()
                core.wait(1)

                responses_in_block = 0
                RT_all_list = []
                accs_in_block = []
                first_trial_in_block = True

            # end of training
            if N == self.settings.trials_in_tBlock + 1:
                if meg_session:
                    self.print_to_screen("Fin de l'entraînement !\n\nReposez-vous.")
                    # stop MEG recordings for recalibration
                    time.sleep(2)
                    port.setData(253)
                    time.sleep(.005)
                    port.setData(0)
                                    
                    press = event.waitKeys(keyList=self.settings.key_resume)
                    if self.settings.key_resume in press:
                        # restart the MEG recordings
                        port.setData(0)
                        time.sleep(.005)
                        port.setData(252)
                        time.sleep(.005)
                        port.setData(0)
                        self.mywindow.flip()
                    self.print_to_screen('Appuyez sur une touche pour lancer la vraie tâche.')
                    press_1 = event.waitKeys(keyList=self.settings.get_key_list())
                    if press_1 in self.settings.get_key_list():
                        self.mywindow.flip()
                else:
                    self.print_to_screen("Fin de l'entraînement.\n\nAppuyez sur Y pour lancer la vraie tache !")
                    press = event.waitKeys(keyList=self.settings.get_key_list())
                    if self.settings.key_quit in press:
                        self.EL_abort()
                        core.quit()

            # end of session
            if N == self.end_at[N - 1]:
                # ending resting state
                if resting_state:
                    self.print_to_screen("Fixez la croix de fixation")
                    core.wait(2)
                    self.mywindow.flip()
                    timer = core.CountdownTimer(self.settings.rs_time)
                    while timer.getTime() > 0:
                        outer.draw()
                        cross.draw()
                        inner.draw()
                        self.mywindow.flip()

                if self.settings.current_session == self.settings.numsessions:
                    self.print_to_screen("Fin de la tâche.\n\nMerci d'avoir participé !")
                else:
                    self.print_to_screen("Fin de la première session.\n\nA demain pour la suite !")
                core.wait(20)
                break

    def run(self, full_screen=full_screen, mouse_visible=mouse_visible, window_gammaErrorPolicy='raise',
            meg_session=meg_session,
            eyetracking=eyetracking):

        # ensure all required folders are created
        ensure_dir(os.path.join(self.workdir_path, "logs"))
        ensure_dir(os.path.join(self.workdir_path, "settings"))
        ensure_dir(os.path.join(self.workdir_path, "sequences"))
        if eyetracking:
            ensure_dir(os.path.join(self.workdir_path, "results"))
            session_folder = os.path.join(self.workdir_path, "results", )

        # load experiment settings if exist or ask the user to specify them
        all_settings_file_path = os.path.join(self.workdir_path, "settings", "settings")
        reminder_file_path = os.path.join(self.workdir_path, "settings", "settings_reminder.txt")
        sequence_file_path = os.path.join(self.workdir_path, "sequences")
        if eyetracking:
            results_folder_path = os.path.join(self.workdir_path, "results")
        self.settings = ExperimentSettings(all_settings_file_path, reminder_file_path, sequence_file_path)
        self.all_settings_def()

        self.pressed_dict = {self.settings.key1: 1, self.settings.key2: 2,
                             self.settings.key3: 3, self.settings.key4: 4,
                             self.settings.key5: 5}

        # create sorted list of stimuli images
        images = []
        files_list = os.listdir(op.join(self.workdir_path, 'stimuli'))
        for img in files_list:
            if '.png' in img:
                images.append(img)
        images.sort()

        # create dictionary matching images and corresponding stimulus number
        if meg_session:
            self.image_dict = {1:op.join(self.workdir_path, 'stimuli', images[0]),
                               2:op.join(self.workdir_path, 'stimuli', images[1])}
        else:
            self.image_dict = {1:op.join(self.workdir_path, 'stimuli', images[0]),
                            2:op.join(self.workdir_path, 'stimuli', images[1]),
                            3:op.join(self.workdir_path, 'stimuli', images[2]),
                            4:op.join(self.workdir_path, 'stimuli', images[3]),
                            5:op.join(self.workdir_path, 'stimuli', images[4])}
        
        # read instruction strings
        inst_feedback_path = os.path.join(self.workdir_path, "inst_and_feedback.txt")
        self.instructions = InstructionHelper(inst_feedback_path)
        self.instructions.read_insts_from_file()
        self.instructions.validate_instructions(self.settings)

        # find out the current subject
        self.participant_id()

        # init window
        self.monitor_settings()
        with visual.Window(size=(screen_width, screen_height), color='grey', fullscr=full_screen,
                           monitor=self.mymonitor, units="pix", gammaErrorPolicy=window_gammaErrorPolicy) as self.mywindow:

            self.mywindow.mouseVisible = mouse_visible

            self.set_audio()

            # check frame rate
            self.frame_check()
            print(self.frame_time)
            print(self.frame_sd)
            print(self.frame_rate)           

            # timer = core.CountdownTimer(5)
            # while timer.getTime() > 0:
            #     self.print_to_screen("Bienvenue !")
            # self.mywindow.flip()

            if eyetracking:
                # initialize EyeLink
                self.EL_init()
                self.open_edf_file()
                self.EL_config()
            
            if meg_session:
                # Start the MEG recordings
                port.setData(0)
                time.sleep(.005)
                port.setData(252)
                time.sleep(.005)
                port.setData(0)


            # show experiment screen
            self.presentation()

            # save user data
            self.person_data.save_person_settings(self)
            self.person_data.append_to_output_file('sessionend_planned_quit')

            # show ending screen
            # self.instructions.show_ending(self)
            
            if eyetracking:
                # disconnect EyeLink
                self.EL_disconnect()

            if meg_session:
                # Stop MEG recordings
                time.sleep(2)
                port.setData(253)
                time.sleep(.005)
                port.setData(0)

if __name__ == "__main__":
    thispath = os.path.split(os.path.abspath(__file__))[0]
    experiment = Experiment(thispath)
    experiment.run()
