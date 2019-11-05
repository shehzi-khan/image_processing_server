import React, { Component } from 'react';
import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import Image from 'react-bootstrap/Image';
import Form from 'react-bootstrap/Form';
import Pagination from 'react-bootstrap/Pagination'
import Table from 'react-bootstrap/Table'

import axios from 'axios';
// import logo from './logo.svg';
import './App.css';

class App extends Component {

    constructor(props) {
        super(props);

        this.state = {
            images: [],
            active_image:null,
            active_classes:null,
            image:null,
            mask:false,
            bbox:false,
            hide_image:false,
            images_per_page:10,
            active_pagination:1,
            pagination_list:[],
            pagination_items:[],
            number_of_images:null,
            active_ann_list:[]
          };

        this.data = [{cat_id:1,category:"student",superb:"person"}]

        this.handlePagination = this.handlePagination.bind(this);
    }


  componentDidMount() {
      let number_of_images=null;
      axios.get(`http://0.0.0.0:5000/images/length`)
          .then(res => {
            let responses = res.data;
            // console.log("Response",responses);
            number_of_images = responses.len;
            this.setState({ number_of_images });
            // console.log("Number of Images",number_of_images);
            this.load_images(this.state.active_pagination,number_of_images)

          });
  }

  imageClick(image){
        this.setState({active_image:image});
      this.load_annotations(image.id);

  }
  load_annotations(id){
        axios.get(`http://0.0.0.0:5000/image/classes?id=`+id)
          .then(res => {
              let response=res.data;
              let active_classes = response.classes;
              this.setState({active_classes});
              let active_ann_list=active_classes.map((item)=>item.seg_id);

              this.setState({active_ann_list});
              console.log(active_classes);
          });
  }

  load_images(active=1,number_of_images=null) {
    let images = [];
    axios.get(`http://0.0.0.0:5000/images`,{
        params:{
            start:active*this.state.images_per_page-this.state.images_per_page,
            end:active*this.state.images_per_page-1
        }
    })
      .then(res => {
        images = res.data;
        this.setState({ images });
        let items=[];
        for (let number = 1; number <= (number_of_images/this.state.images_per_page)+1; number++) {
          items.push(
            <Pagination.Item key={number} active={number === active} onClick={this.handlePagination}>
              {number}
            </Pagination.Item>,
          );
        }
        this.setState({pagination_list:items});
        // console.log(this.state.images);
        this.setState({active_image:images[0]});
        this.load_annotations(images[0].id)
      });

  }
  handlePagination(event){
      event.preventDefault();
      this.setState({active_pagination: Number(event.target.text)});
      // console.log(this.state.active_pagination);
      this.load_images(Number(event.target.text),this.state.number_of_images)
  }

  renderPagination() {
    return (
      <Pagination bsSize="small" >{this.state.pagination_list}</Pagination>
    );
  }

  updateAnnList(class_item){
        if(this.state.active_ann_list.some(item => class_item.seg_id === item)){
              var array = [...this.state.active_ann_list]; // make a separate copy of the array
              var index = array.indexOf(class_item.seg_id);
              if (index !== -1) {
                array.splice(index, 1);
                this.setState({active_ann_list: array});
            }
        }
        else{
            var array = [...this.state.active_ann_list];
            array.push(class_item.seg_id);
            this.setState({active_ann_list: array});
        }

        console.log(this.state.active_ann_list)
  }


  renderAnnotations(){
        if (this.state.active_classes != null){
            return this.state.active_classes.map((class_item,index) => {
                return (
                    <tr id={class_item.seg_id}>
                        <td> <Form.Check defaultChecked onClick={()=>this.updateAnnList(class_item)} type={"checkbox"} label={index+1} /> </td>
                        <td> {class_item.cat_id} </td>
                        <td> {class_item.category} </td>
                        <td> {class_item.super} </td>
                    </tr>
                )

            })
        }
  }

  render() {
    // this.load_images()
    return (
      <Container>
          <Row>
            <Col className={"Image-list"}>
                <Container >
                    { this.state.images.map(image => <Col fluid onClick={()=>{this.imageClick(image)}}><Image fluid src={"http://localhost:5000/thumbs?file_name="+image.file_name} thumbnail /></Col>)}
              </Container>
                <Container>
                    <Pagination bssize="small" >{this.state.pagination_list}</Pagination>
                </Container>
            </Col>
            <Col >
                <Row>
                    <Image fluid onChange={()=>console.log("hello")} src={!!(this.state.active_image)?"http://localhost:5000/image?file_name="+this.state.active_image.file_name+"&mask="+this.state.mask+"&bbox="+this.state.bbox+"&hide_image="+this.state.hide_image+"&ann="+this.state.active_ann_list:""} thumbnail />
                </Row>
                <Row>
                    <Form>
                        <Form.Row>
                            <Form.Check onClick={()=>this.setState(prevState => ({  mask: !prevState.mask}))} type={"checkbox"} label={`Show Mask`} />
                            <Form.Check  onClick={()=>this.setState(prevState => ({  bbox: !prevState.bbox}))} type={"checkbox"} label={`Show Bounding Box`} />
                            <Form.Check  onClick={()=>this.setState(prevState => ({  hide_image: !prevState.hide_image}))} type={"checkbox"} label={`Hide Original Image`} />
                        </Form.Row>
                    </Form>
                </Row>
                <Row>
                    <Col>{!!(this.state.active_image)?this.state.active_image.file_name:""}</Col>
                </Row>
                <Row>
                    <Form>
                        <Table striped bordered hover>
                          <thead>
                            <tr>
                              <th>#</th>
                              <th>Class ID</th>
                              <th>Class</th>
                              <th>Super Class</th>
                            </tr>
                          </thead>
                          <tbody>
                           {this.renderAnnotations()}
                          </tbody>
                    </Table>
                    </Form>
                </Row>

            </Col>
          </Row>

        </Container>
    );
  }
}

export default App;
