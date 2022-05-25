import React, { useState } from 'react';
import { AppShell, Header, Title, Select, Container, Grid, Group, ActionIcon, TextInput, Text, Button, Center, Table } from '@mantine/core';
import data from "./game_data.json";
import { useForm, formList } from '@mantine/form';
import { randomId } from '@mantine/hooks';
import { Trash } from 'tabler-icons-react';
import axios from 'axios';

function App() {

  const form = useForm({
    initialValues: {
      games: formList([{ game_index: '', hours_played: '', key: randomId() }]),
    },
  });

  const [reccomendations, setReccomendations] = useState([]);
  const [table, setTable] = useState(false);

  const elements = ["2","4","500", "300", "200"];
  // Will  populate the rows in the table

  const fields = form.values.games.map((item, index) => (
    
      <Grid key={index}>
      <Grid.Col span={8}>
        <Select
          placeholder="Pick one"
          data={data}
          searchable
          {...form.getListInputProps('games', index, 'game_index')}
        />
        </Grid.Col>
        <Grid.Col span={2}>
        <TextInput
        placeholder="Hours Played"
        required
        sx={{ flex: 1 }}
        {...form.getListInputProps('games', index, 'hours_played')}
      />
      </Grid.Col>
      <Grid.Col span={2}>
      <Center>
      <ActionIcon
        color="red"
        variant="hover"
        onClick={() => form.removeListItem('games', index)}
      >
        <Trash size={16} />
      </ActionIcon>
      </Center>
      </Grid.Col>
    </Grid>
  ));

  return (
    <AppShell
      padding="md"
      fixed
      header={<Header height={80} p="xs"><Title align='center' my='sm' order={3}>Steam Games Recommender System</Title></Header>}
      styles={(theme) => ({
        main: { backgroundColor: theme.colorScheme === 'dark' ? theme.colors.dark[8] : theme.colors.gray[0] },
      })}
    >
      <Container>
        {
          table &&
      <Table>
      <thead>
        <tr>
          <th>Sr.No</th>
          <th>Recommendations</th>
        </tr>
      </thead>
      <tbody>{reccomendations.map((element, index) => (
    <tr key={index}>
      <td>{index + 1}</td>
      <td>{data[element].label}</td>
    </tr>
  ))}</tbody>
    </Table>
}
      {fields.length > 0 ? (
        <Grid mt={50}>
          <Grid.Col span={8}>
          <Text weight={500} sx={{ flex: 1 }}>
            Games
          </Text>
          </Grid.Col>
          <Grid.Col span={2}>
          <Text weight={500}>
            Hours Played
          </Text>
          </Grid.Col>
          <Grid.Col span={2}>
            <Center>
          <Text weight={500}>
            Delete
          </Text>
          </Center>
          </Grid.Col>
        </Grid>
      ) : (
        <Text color="dimmed" align="center" mt={50}>
          No one here...
        </Text>
      )}

      {fields}
      
      <Group position="center" mt="md">
        <Button
          onClick={() =>
            form.addListItem('games', { game_index: '', hours_played: '', key: randomId() })
          }
        >
          Add Games
        </Button>
      </Group>
      <Center>
        <Button mt={25} color="green" onClick={form.onSubmit((values)=>{
          console.log(values);
          let d = new Set()
          let flag = false
          for(let item of  values.games)
          {
            if(! flag && d.has(item.game_index))
            {
              flag = true
              alert("Duplication Error!!!!")
              break
            }
            else
            {
              d.add(item.game_index)
            }
            
          }
          axios.post("http://127.0.0.1:5000/predict", values, {
            headers: {
              "Access-Control-Allow-Origin": "*"
            }
          }).then((data) => {
            console.log(data.data.result);
            setReccomendations(data.data.result);
            setTable(true);
            
          })
        })}>
        Get Recommendations
      </Button>
        </Center>
      </Container>
      
    </AppShell>
  );
}

export default App;
