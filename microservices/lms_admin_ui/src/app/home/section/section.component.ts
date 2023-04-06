import { Component, OnInit, ViewChild, Inject } from '@angular/core';
import { Location } from '@angular/common';
import { LiveAnnouncer } from '@angular/cdk/a11y';
import { MatSort, Sort } from '@angular/material/sort';
import { MatLegacyTableDataSource as MatTableDataSource } from '@angular/material/legacy-table'
import { MatLegacyDialog as MatDialog, MAT_LEGACY_DIALOG_DATA as MAT_DIALOG_DATA, MatLegacyDialogRef as MatDialogRef } from '@angular/material/legacy-dialog'
import { CreateSectionComponent } from '../create-section/create-section.component';
import { HomeService } from '../service/home.service';
import { Router, NavigationStart, NavigationEnd, Event as NavigationEvent } from '@angular/router';
import { InviteStudentModalComponent } from '../invite-student-modal/invite-student-modal.component';

interface LooseObject {
  [key: string]: any
}

export interface staff {
  name: string;
  email: string;
  role: string;
}

export interface student {
  first_name: string;
  last_name: string;
  email: string;
  created_time: string;
}

@Component({
  selector: 'app-section',
  templateUrl: './section.component.html',
  styleUrls: ['./section.component.scss']
})
export class SectionComponent implements OnInit {
  selectedSection: any
  displayedColumns: string[] = ['email', 'role'];
  studentDisplayedColumns: string[] = ['first name', 'last name', 'email', 'created time','status','action'];

  tableData: staff[] = []
  studentTableData: student[] = []
  dataSource = new MatTableDataSource(this.tableData);

  cohortDetails: any
  courseTemplateDetails: any
  sectionDetails: any[] = []
  loadCard: boolean = false
  loadSection: boolean = false
  studentTableLoader:boolean=true
  constructor(private _liveAnnouncer: LiveAnnouncer, public dialog: MatDialog, public _HomeService: HomeService, 
    public router: Router, private _location: Location) { }
  @ViewChild(MatSort) sort: MatSort;


  ngOnInit(): void {
    this.dataSource.sort = this.sort;
    let id
    console.log(this.router.url)
    id = this.router.url.split('/')[2]
    this.getCohortDetails(id)
  }

  getCohortDetails(id: any) {
    this.loadCard = true
    this.loadSection = true
    this._HomeService.getCohort(id).subscribe((res: any) => {
      this.cohortDetails = res
      console.log('cohort details', this.cohortDetails)
      this.getCourseTemplateDetails(res.course_template.split('/')[1])
    })
  }
  getCourseTemplateDetails(id: any) {
    this._HomeService.getCourseTemplate(id).subscribe((res: any) => {
      this.courseTemplateDetails = res
      this.loadCard = false
      console.log('course template', this.courseTemplateDetails)
      this.getSectionList(this.cohortDetails.id)
    })
  }

  getSectionList(cohortid: any) {
    this.loadSection = true
    this._HomeService.getSectionList(cohortid).subscribe((res: any) => {
      this.sectionDetails = res.data
      if (this.sectionDetails.length > 0) {
        if (location.pathname.split('/' )[3]) {
          console.log('if router url split',this.router.url.split('/'))
          this.selectedSection = this.sectionDetails.find(o => o.id == location.pathname.split('/')[3])
          console.log('selected sec', this.selectedSection )
        }
        else {
          this.selectedSection = this.sectionDetails[0]
        }
        this.createTableData()
      }
      this.loadSection = false
      // console.log('section', this.sectionDetails)
    })
  }

  openClassroom() {
    window.open(this.selectedSection.classroom_url
      , '_blank');
  }
  getSectionStudents() {
    this.studentTableLoader = true
    this._HomeService.getStudentsInSection(this.selectedSection.id).subscribe((res: any) => {
      this.studentTableData = []
      this.studentTableData = res.data
      console.log('student data', this.studentTableData)
      this.studentTableLoader = false
    },
    (err:any)=>{
      this.studentTableLoader = false
    }
    )
  }

  updateUrl(url: string) {
    console.log('path',location.pathname)
    let pathArr = location.pathname.split('/')
    if(pathArr.length == 4){
      pathArr[3] = url
    }
    else{
      pathArr.push(url)
    }
    console.log(pathArr.toString().replace(/,/g,'/'))
    this._location.go(pathArr.toString().replace(/,/g,'/'))
  }

  createTableData() {
    console.log('selected sec', this.selectedSection)
    this.updateUrl(this.selectedSection.id)
    this.getSectionStudents()
    this.tableData = []
    for (let x of this.selectedSection.teachers) {
      let staffObj: staff = { name: '', email: '', role: '' }
      staffObj.name = 'TBD'
      staffObj.email = x
      if (x == this.courseTemplateDetails.admin) {
        staffObj.role = 'Admin'
      }
      else if (x == this.courseTemplateDetails.instructional_designer) {
        staffObj.role = 'Instructional Designer'
      }
      else {
        staffObj.role = 'Teaching Staff'
      }
      this.tableData.push(staffObj)
    }
    console.log('table data', this.tableData)

  }

  announceSortChange(sortState: Sort) {
    if (sortState.direction) {
      this._liveAnnouncer.announce(`Sorted ${sortState.direction}ending`);
    } else {
      this._liveAnnouncer.announce('Sorting cleared');
    }
  }

  openCreateSectionDialog(): void {
    let tempObj: LooseObject = {}
    tempObj['cohort_name'] = this.cohortDetails.name
    tempObj['course_template_name'] = this.courseTemplateDetails.name
    tempObj['cohort_id'] = this.cohortDetails.id
    tempObj['course_template_id'] = this.courseTemplateDetails.id
    tempObj['instructional_desiner'] = this.courseTemplateDetails.instructional_designer
    tempObj['admin'] = this.courseTemplateDetails.admin


    let sectionModalData: LooseObject = {}
    sectionModalData['mode'] = 'Create'
    sectionModalData['init_data'] = ''
    sectionModalData['extra_data'] = tempObj

    const dialogRef = this.dialog.open(CreateSectionComponent, {
      width: '500px',
      data: sectionModalData
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result.data == 'success') {
        this.getSectionList(this.cohortDetails.id)
      }
    });
  }

  openEditSelectionDialog(): void {
    let tempObj: LooseObject = {}
    tempObj['cohort_name'] = this.cohortDetails.name
    tempObj['course_template_name'] = this.courseTemplateDetails.name
    tempObj['cohort_id'] = this.cohortDetails.id
    tempObj['course_template_id'] = this.courseTemplateDetails.id
    tempObj['instructional_desiner'] = this.courseTemplateDetails.instructional_designer
    tempObj['admin'] = this.courseTemplateDetails.admin
    tempObj['section_id'] = this.selectedSection.id
    tempObj['section'] = this.selectedSection.section
    tempObj['description'] = this.selectedSection.description
    tempObj['classroom_id'] = this.selectedSection.classroom_id
    tempObj['teachers'] = []
    for (let x of this.selectedSection.teachers) {
      if (x != this.courseTemplateDetails.admin && x != this.courseTemplateDetails.instructional_designer) {
        tempObj['teachers'].push(x)
      }
    }

    let sectionModalData: LooseObject = {}
    sectionModalData['mode'] = 'Edit'
    sectionModalData['init_data'] = tempObj
    sectionModalData['extra_data'] = ''

    const dialogRef = this.dialog.open(CreateSectionComponent, {
      width: '500px',
      data: sectionModalData
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result.data == 'success') {
        this.getSectionList(this.cohortDetails.id)
      }
    });
  }

  openDeleteDialog(firstName: any, lastName: any, userId: any) {
    let deleteDialogData: LooseObject = {}
    deleteDialogData['first_name'] = firstName
    deleteDialogData['last_name'] = lastName
    deleteDialogData['section'] = this.selectedSection.section
    deleteDialogData['user_id'] = userId
    deleteDialogData['section_id'] = this.selectedSection.id
    const dialogRef = this.dialog.open(DeleteOverviewDialog, {
      width: '500px',
      data: deleteDialogData
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result.data == 'success') {
        this.getSectionStudents()
      }
    });
  }

  openInviteStudentDialog(){
    console.log('selected sec',this.selectedSection)
    let tempObj: LooseObject = {}
    tempObj['cohort_name'] = this.cohortDetails.name
    tempObj['section'] = this.selectedSection.section
    tempObj['section_id'] = this.selectedSection.id

    let inviteStudentModalData: LooseObject = {}
    inviteStudentModalData['mode'] = 'Section'
    inviteStudentModalData['init_data'] = tempObj
    inviteStudentModalData['extra_data'] = ''
    const dialogRef = this.dialog.open(InviteStudentModalComponent, {
      width: '500px',
      data: inviteStudentModalData
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result.data == 'success') {
        this.getSectionStudents()
      }
    });
  }

}

@Component({
  selector: 'delete-overview-dialog',
  templateUrl: 'delete-overview-dialog.html',
})
export class DeleteOverviewDialog {
  constructor(
    public dialogRef: MatDialogRef<DeleteOverviewDialog>,
    @Inject(MAT_DIALOG_DATA) public deleteDialogData: any, public _HomeService: HomeService
  ) { }

  deleteStudent() {
    this._HomeService.deleteStudent(this.deleteDialogData.user_id, this.deleteDialogData.section_id).subscribe((res: any) => {
      if (res.success == true) {
        this.dialogRef.close({ data: 'success' });
      }
    })
  }

  onNoClick(): void {
    this.dialogRef.close({ data: 'closed' });
  }
}
