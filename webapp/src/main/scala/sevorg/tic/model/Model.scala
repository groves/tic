package sevorg.tic.model

import javax.persistence.{EntityManager,Persistence}

import scala.collection.jcl.{BufferWrapper,SetWrapper}

object Model {
  val emVar = new ThreadLocal[EntityManager];
  def em = emVar.get();
  implicit def setToWrapper[A](set : java.util.Set[A]) = new SetWrapper[A]{override def underlying = set}
  implicit def listToWrapper[A](list : java.util.List[A]) = new BufferWrapper[A]{override def underlying = list}
}

