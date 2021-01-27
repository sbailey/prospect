# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
=======================
prospect.viewerVIWidgetSet
=======================

Class containing bokeh widgets related to visual inspection

"""


from bokeh.models.widgets import (
    TextInput, CheckboxGroup, Select, RadioButtonGroup, Div, 
    TableColumn, DataTable, Toggle)

from .utilities import get_resources, vi_flags, vi_file_fields, vi_spectypes, vi_std_comments


class viewerVIWidgetSet(object):
    """ 
    Encapsulates Bokeh widgets, and related callbacks, used for VI
    """
    
    def __init__(self, viewer_plotset, title):
        self.vi_class_labels = [ x["label"] for x in vi_flags if x["type"]=="class" ]
        self.vi_issue_labels = [ x["label"] for x in vi_flags if x["type"]=="issue" ]
        self.vi_issue_slabels = [ x["shortlabel"] for x in vi_flags if x["type"]=="issue" ]
        self.js_files = get_resources('js')
        self.title = title
        
        self.vi_countdown_toggle = None
        

    def add_filename(self, username=''):
        #- VI file name
        default_vi_filename = "desi-vi_"+title
        if username.strip()!="" :
            default_vi_filename += ("_"+username)
        else :
            default_vi_filename += "_unknown-user"
        default_vi_filename += ".csv"
        self.vi_filename_input = TextInput(value=default_vi_filename, title="VI file name:")


    def add_vi_issues(self, viewer_cds, viewer_widgets):
        #- Optional VI flags (issues)
        self.vi_issue_input = CheckboxGroup(labels=self.vi_issue_labels, active=[])
        vi_issue_code = self.js_files["CSVtoArray.js"] + self.js_files["save_vi.js"]
        vi_issue_code += """
            var issues = []
            for (var i=0; i<vi_issue_labels.length; i++) {
                if (vi_issue_input.active.indexOf(i) >= 0) issues.push(vi_issue_slabels[i])
            }
            if (issues.length > 0) {
                cds_targetinfo.data['VI_issue_flag'][ifiberslider.value] = ( issues.join('') )
            } else {
                cds_targetinfo.data['VI_issue_flag'][ifiberslider.value] = " "
            }
            autosave_vi_localStorage(vi_file_fields, cds_targetinfo.data, title)
            cds_targetinfo.change.emit()
            """
        self.vi_issue_callback = CustomJS(
            args=dict(cds_targetinfo = viewer_cds.cds_targetinfo,
                      ifiberslider = viewer_widgets.ifiberslider,
                      vi_issue_input = self.vi_issue_input,
                      vi_issue_labels = self.vi_issue_labels,
                      vi_issue_slabels = self.vi_issue_slabels,
                      title = self.title, vi_file_fields = vi_file_fields),
                      code = vi_issue_code )
        self.vi_issue_input.js_on_click(self.vi_issue_callback)


    def add_vi_z(self, viewer_cds, viewer_widgets):
    ## TODO: z2vi behaviour if with_vi_widget=False ..?
        #- Optional VI information on redshift
        self.vi_z_input = TextInput(value='', title="VI redshift:")
        vi_z_code = self.js_files["CSVtoArray.js"] + self.js_files["save_vi.js"]
        vi_z_code += """
            cds_targetinfo.data['VI_z'][ifiberslider.value]=vi_z_input.value
            autosave_vi_localStorage(vi_file_fields, cds_targetinfo.data, title)
            cds_targetinfo.change.emit()
            """
        self.vi_z_callback = CustomJS(
            args=dict(cds_targetinfo = viewer_cds.cds_targetinfo,
                      ifiberslider = viewer_widgets.ifiberslider,
                      vi_z_input = self.vi_z_input,
                      title = self.title, vi_file_fields=vi_file_fields),
                      code = vi_z_code )
        self.vi_z_input.js_on_change('value', self.vi_z_callback)

        # Copy z value from redshift slider to VI
        self.z_tovi_button = Button(label='Copy z to VI')
        self.z_tovi_callback = CustomJS(
            args=dict(z_input=viewer_widgets.z_input, vi_z_input=self.vi_z_input),
            code="""
                vi_z_input.value = z_input.value
            """)
        self.z_tovi_button.js_on_event('button_click', self.z_tovi_callback)

    def add_vi_spectype(self, viewer_cds, viewer_widgets):
        #- Optional VI information on spectral type
        self.vi_category_select = Select(value=' ', title="VI spectype:", options=([' '] + vi_spectypes))
        # The default value set to ' ' as setting value='' does not seem to work well with Select.
        vi_category_code = self.js_files["CSVtoArray.js"] + self.js_files["save_vi.js"]
        vi_category_code += """
            if (vi_category_select.value == ' ') {
                cds_targetinfo.data['VI_spectype'][ifiberslider.value]=''
            } else {
                cds_targetinfo.data['VI_spectype'][ifiberslider.value]=vi_category_select.value
            }
            autosave_vi_localStorage(vi_file_fields, cds_targetinfo.data, title)
            cds_targetinfo.change.emit()
            """
        self.vi_category_callback = CustomJS(
            args=dict(cds_targetinfo=viewer_cds.cds_targetinfo, 
                      ifiberslider = viewer_widgets.ifiberslider,
                      vi_category_select=self.vi_category_select,
                      title=self.title, vi_file_fields=vi_file_fields),
            code=vi_category_code )
        self.vi_category_select.js_on_change('value', self.vi_category_callback)


    def add_vi_comment(self, viewer_cds, viewer_widgets):
        #- Optional VI comment
        self.vi_comment_input = TextInput(value='', title="VI comment (see guidelines):")
        vi_comment_code = self.js_files["CSVtoArray.js"] + self.js_files["save_vi.js"]
        vi_comment_code += """
            var stored_comment = (vi_comment_input.value).replace(/./g, function(char){
                if ( char==',' ) {
                    return ';'
                } else if ( char.charCodeAt(0)<=127 ) {
                    return char
                } else {
                    var char_list = ['Å','α','β','γ','δ','λ']
                    var char_replace = ['Angstrom','alpha','beta','gamma','delta','lambda']
                    for (var i=0; i<char_list.length; i++) {
                        if ( char==char_list[i] ) return char_replace[i]
                    }
                    return '?'
                }
            })
            cds_targetinfo.data['VI_comment'][ifiberslider.value] = stored_comment
            autosave_vi_localStorage(vi_file_fields, cds_targetinfo.data, title)
            cds_targetinfo.change.emit()
            """
        self.vi_comment_callback = CustomJS(
            args=dict(cds_targetinfo = viewer_cds.cds_targetinfo,
                      ifiberslider = viewer_widgets.ifiberslider, 
                      vi_comment_input = self.vi_comment_input,
                      title=self.title, vi_file_fields=vi_file_fields),
            code=vi_comment_code )
        self.vi_comment_input.js_on_change('value',self.vi_comment_callback)

        #- List of "standard" VI comment
        self.vi_std_comment_select = Select(value=" ", title="Standard comment:", options=([' '] + vi_std_comments))
        vi_std_comment_code = """
            if (vi_std_comment_select.value != ' ') {
                if (vi_comment_input.value != '') {
                    vi_comment_input.value = vi_comment_input.value + " " + vi_std_comment_select.value
                } else {
                    vi_comment_input.value = vi_std_comment_select.value
                }
            }
            """
        self.vi_std_comment_callback = CustomJS(
            args = dict(vi_std_comment_select = self.vi_std_comment_select,
                        vi_comment_input = self.vi_comment_input),
                        code = vi_std_comment_code )
        self.vi_std_comment_select.js_on_change('value', self.vi_std_comment_callback)


    def add_vi_classification(self, viewer_cds, viewer_widgets):
        #- Main VI classification
        self.vi_class_input = RadioButtonGroup(labels=self.vi_class_labels)
        vi_class_code = self.js_files["CSVtoArray.js"] + self.js_files["save_vi.js"]
        vi_class_code += """
            if ( vi_class_input.active >= 0 ) {
                cds_targetinfo.data['VI_class_flag'][ifiberslider.value] = vi_class_labels[vi_class_input.active]
                //if ( vi_class_labels[vi_class_input.active]=="4" && model) { // Flag '4' => VI_z = z_pipe (if available)
                //    var z = targetinfo.data['z'][ifiberslider.value]
                //    vi_z_input.value = parseFloat(z).toFixed(4)
                //    vi_category_select.value = targetinfo.data['spectype'][ifiberslider.value]
                //}
            } else {
                cds_targetinfo.data['VI_class_flag'][ifiberslider.value] = "-1"
            }
            autosave_vi_localStorage(vi_file_fields, cds_targetinfo.data, title)
            cds_targetinfo.change.emit()
        """
        self.vi_class_callback = CustomJS(
            args = dict(cds_targetinfo = viewer_cds.cds_targetinfo,
                        vi_class_input = self.vi_class_input,
                        vi_class_labels = vi_class_labels,
                        ifiberslider = viewer_widgets.ifiberslider,
                        title=self.title, vi_file_fields = vi_file_fields,
                        targetinfo = viewer_cds.cds_targetinfo,
                        model = viewer_cds.cds_model, vi_z_input=self.vi_z_input,
                        vi_category_select=self.vi_category_select),
                        code=vi_class_code )
        self.vi_class_input.js_on_click(self.vi_class_callback)

    def add_vi_scanner(self, viewer_cds, nspec):
        ## TODO nspec arg ??
        #- VI scanner name
        self.vi_name_input = TextInput(value=(viewer_cds.cds_targetinfo.data['VI_scanner'][0]).strip(), title="Your name (3-letter acronym):")
        vi_name_code = self.js_files["CSVtoArray.js"] + self.js_files["save_vi.js"]
        vi_name_code += """
            for (var i=0; i<nspec; i++) {
                cds_targetinfo.data['VI_scanner'][i]=vi_name_input.value
            }
            var newname = vi_filename_input.value
            var pepe = newname.split("_")
            newname = ( pepe.slice(0,pepe.length-1).join("_") ) + ("_"+vi_name_input.value+".csv")
            vi_filename_input.value = newname
            autosave_vi_localStorage(vi_file_fields, cds_targetinfo.data, title)
            """
        self.vi_name_callback = CustomJS(
            args = dict(cds_targetinfo = viewer_cds.cds_targetinfo,
                        nspec = nspec, 
                        vi_name_input = self.vi_name_input,
                        vi_filename_input = self.vi_filename_input, title=self.title,
                        vi_file_fields = vi_file_fields),
                        code=vi_name_code )
        self.vi_name_input.js_on_change('value', self.vi_name_callback)

    def add_guidelines(self):
        #- Guidelines for VI flags
        vi_guideline_txt = "<B> VI guidelines </B>"
        vi_guideline_txt += "<BR /> <B> Classification flags: </B>"
        for flag in vi_flags :
            if flag['type'] == 'class' : vi_guideline_txt += ("<BR />&emsp;&emsp;[&emsp;"+flag['label']+"&emsp;] "+flag['description'])
        vi_guideline_txt += "<BR /> <B> Optional indications: </B>"
        for flag in vi_flags :
            if flag['type'] == 'issue' :
                vi_guideline_txt += ( "<BR />&emsp;&emsp;[&emsp;" + flag['label'] +
                                     "&emsp;(" + flag['shortlabel'] + ")&emsp;] " + flag['description'] )
        vi_guideline_txt += "<BR /> <B> Comments: </B> <BR /> 100 characters max, avoid commas (automatically replaced by semi-columns), ASCII only."
        self.vi_guideline_div = Div(text=vi_guideline_txt)

    def add_vi_storage(self, viewer_cds):
        #- Save VI info to CSV file
        self.save_vi_button = Button(label="Download VI", button_type="success")
        save_vi_code = self.js_files["FileSaver.js"] + self.js_files["CSVtoArray.js"] + self.js_files["save_vi.js"]
        save_vi_code += """
            download_vi_file(vi_file_fields, cds_targetinfo.data, vi_filename_input.value)
            """
        self.save_vi_callback = CustomJS(
            args = dict(cds_targetinfo = viewer_cds.cds_targetinfo,
                        vi_file_fields = vi_file_fields,
                        vi_filename_input = self.vi_filename_input),
                        code=save_vi_code )
        self.save_vi_button.js_on_event('button_click', self.save_vi_callback)

        #- Recover auto-saved VI data in browser
        self.recover_vi_button = Button(label="Recover auto-saved VI", button_type="default")
        recover_vi_code = self.js_files["CSVtoArray.js"] + self.js_files["recover_autosave_vi.js"]
        self.recover_vi_callback = CustomJS(
            args = dict(title=self.title, vi_file_fields=vi_file_fields,
                        cds_targetinfo = viewer_cds.cds_targetinfo,
                        ifiber = ifiberslider.value, vi_comment_input = self.vi_comment_input,
                        vi_name_input=self.vi_name_input, vi_class_input=self.vi_class_input,
                        vi_issue_input=self.vi_issue_input,
                        vi_issue_slabels=self.vi_issue_slabels, vi_class_labels=self.vi_class_labels),
                        code = recover_vi_code )
        self.recover_vi_button.js_on_event('button_click', self.recover_vi_callback)

        #- Clear all auto-saved VI
        self.clear_vi_button = Button(label="Clear all auto-saved VI", button_type="default")
        self.clear_vi_callback = CustomJS( args = dict(), code = """
            localStorage.clear()
            """ )
        self.clear_vi_button.js_on_event('button_click', self.clear_vi_callback)

    def add_vi_table(self, viewer_cds):
        #- Show VI in a table
        vi_table_columns = [
            TableColumn(field="VI_class_flag", title="Flag", width=40),
            TableColumn(field="VI_issue_flag", title="Opt.", width=50),
            TableColumn(field="VI_z", title="VI z", width=50),
            TableColumn(field="VI_spectype", title="VI spectype", width=150),
            TableColumn(field="VI_comment", title="VI comment", width=200)
        ]
        self.vi_table = DataTable(source=viewer_cds.cds_targetinfo, columns=vi_table_columns, width=500)
        self.vi_table.height = 10 * self.vi_table.row_height


    def add_countdown(self, vi_countdown):
        #- VI countdown
        assert vi_countdown > 0
        self.vi_countdown_callback = CustomJS(args=dict(vi_countdown=vi_countdown), code="""
            if ( (cb_obj.label).includes('Start') ) { // Callback doesn't do anything after countdown started
                var countDownDate = new Date().getTime() + (1000 * 60 * vi_countdown);
                var countDownLoop = setInterval(function(){
                    var now = new Date().getTime();
                    var distance = countDownDate - now;
                    if (distance<0) {
                        cb_obj.label = "Time's up !";
                        clearInterval(countDownLoop);
                    } else {
                        var days = Math.floor(distance / (1000 * 60 * 60 * 24));
                        var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                        var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                        //var stuff = days + "d " + hours + "h " + minutes + "m " + seconds + "s ";
                        var stuff = minutes + "m " + seconds + "s ";
                        cb_obj.label = "Countdown: " + stuff;
                    }
                }, 1000);
            }
        """)
        self.vi_countdown_toggle = Toggle(label='Start countdown ('+str(vi_countdown)+' min)', active=False, button_type="success")
        self.vi_countdown_toggle.js_on_change('active', self.vi_countdown_callback)
    