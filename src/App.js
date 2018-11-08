import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import Welcome from './Welcome';
import scam_info from './scam_info';

class App extends Component {


    foo() {
        console.log("running foo");
        // this.person_name = "hello";
        this.setState({ person_name: "new name" });
    }

    componentWillMount() {
        const clean_wallets = ['1', '9w384759w4', '29043857092845', '384w759823745', '9834759823754']
        const dirty_wallets = ['0', '9w384759w4', '29043857092845', '384w759823745', '9834759823754']

        const results = scam_info["result"];

        // this.person_name = "default_name";
        this.setState({ person_name: "default name", address:"0x39857394857", clean:false });
        // this.person_name = "default_name"
      }    

  

  render() {

    return (
      <div className="App">
        
        <div>
            <Welcome 
                name={this.state.person_name} 
                foofunc={() => this.setState({person_name:"new2 name"})} 
                address={this.state.address}
                clean={this.state.clean}
            />
        </div>
      </div>
    );
  }
}

export default App;
