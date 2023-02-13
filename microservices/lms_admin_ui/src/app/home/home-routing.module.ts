import { HomeComponent } from './home.component';
import { SectionComponent } from './section/section.component';

import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

const routes: Routes = [
    {
        path: '',
        component: HomeComponent,
    },
    {
        path: ':id',
        component: SectionComponent,
    },
    {
        path: ':id/:id',
        component: SectionComponent,
    }
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule]
})
export class HomeRoutingModule { }